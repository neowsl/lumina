import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

EDSTEM_TOKEN = os.getenv("EDSTEM_TOKEN")

if not EDSTEM_TOKEN:
    print("ERROR: EDSTEM_TOKEN not found in .env file")

SECTIONS_FILE = "data/sections.json"
SCHEMA_FILE = "data/schema.json"
MODEL_PATH = "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf"

HEADERS = {"X-Token": EDSTEM_TOKEN, "Accept": "application/json"}

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4, verbose=False)


def fetch_edstem_content(lesson_id: str) -> dict:
    url = f"https://us.edstem.org/api/lessons/{lesson_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json()


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for s in soup(["script", "style", "video"]):
        s.decompose()
    return soup.get_text(separator=" ", strip=True)


def generate_metadata_llm(text: str, title: str) -> dict:
    prompt = f"""<|start_header_id|>system<|end_header_id|>
        You are a Senior TA for UW CSE 122. Analyze Java problems and return ONLY a JSON object.

        ### DIFFICULTY RUBRIC:
        - easy: Review of CSE 121 (Basic loops, Scanner, simple Arrays, Strings).
        - medium: Core CSE 122 topics (Lists, Stacks, Queues, basic OOP, File I/O).
        - hard: Advanced topics (Sets, Maps, custom Classes, Interfaces, complex decomposition).

        ### ALLOWED CONCEPTS (Pick 1-3 most relevant, lowercase):
        [arrays, lists, stacks, queues, sets, maps, oop, interfaces, file_io, loops, conditionals, logic, strings]

        ### OUTPUT FORMAT:
        {{"concepts": ["concept1", "concept2"], "difficulty": "Level"}}<|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        Analyze this problem:
        Title: {title}
        Content: {text[:1000]}
        JSON Result:<|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>"""

    output = llm(prompt, max_tokens=150, stop=["<|eot_id|>"], echo=False)
    raw_response = output["choices"][0]["text"].strip()

    try:
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        return json.loads(raw_response[start:end])
    except:
        return {"concepts": ["Unknown"], "difficulty": "Unknown"}


def main():
    if not os.path.exists(SECTIONS_FILE):
        print("ERROR: Missing sections file")

    with open(SECTIONS_FILE, "r") as f:
        sections = json.load(f)

    res = []

    for section in sections:
        print(f"Processing Section: {section['title']}...")

        data = fetch_edstem_content(section["id"])
        if not data:
            print("WARN: Failed to fetch page")
            continue

        slides = data["lesson"].get("slides", [])

        for slide in slides:
            if slide.get("type") != "code":
                continue

            problem_title = slide.get("title")

            print(f"  > Processing Problem: {problem_title}...")

            clean_text = clean_html(slide.get("content", ""))

            meta = generate_metadata_llm(clean_text, problem_title)

            res.append(
                {
                    "lesson_id": section["id"],
                    "slide_id": slide.get("id"),
                    "title": problem_title,
                    "concepts": meta.get("concepts", []),
                    "difficulty": meta.get("difficulty", "Unknown"),
                    "url": f"{section['url']}/slides/{slide.get('id')}",
                }
            )

        # save after each iteration
        with open(SCHEMA_FILE, "w") as f:
            json.dump(res, f, indent=4)


if __name__ == "__main__":
    main()
