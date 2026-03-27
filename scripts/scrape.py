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

TARGETS_FILE = "data/sections.json"
OUTPUT_FILE = "data/schema.json"
MODEL_PATH = "models/llama-3-8b.gguf"

HEADERS = {"Authorization": f"Bearer {EDSTEM_TOKEN}", "Accept": "application/json"}

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)


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
    for s in soup(["script", "style"]):
        s.decompose()
    return soup.get_text(separator=" ", strip=True)


def generate_metadata_llm(text: str, title: str) -> dict:
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a CS Education Assistant. Analyze the content and return ONLY a JSON object.
    Structure: {{"concepts": [], "difficulty": ""}}<|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Title: {title}
    Content: {text[:1200]}
    JSON output:<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    output = llm(prompt, max_tokens=150, stop=["<|eot_id|>"], echo=False)
    raw_response = output["choices"][0]["text"].strip()

    try:
        # Basic cleanup in case the LLM adds markdown backticks
        clean_json = raw_response.split("{")[-1].split("}")[0]
        return json.loads("{" + clean_json + "}")
    except:
        return {"concepts": ["Unknown"], "difficulty": "Unknown"}


def main():
    with open(TARGETS_FILE, "r") as f:
        targets = json.load(f)

    res = []

    for target in targets:
        print(f"Processing {target['title']}...")

        data = fetch_edstem_content(target["id"])
        if not data:
            print("WARN: Failed to fetch page")
            continue

        # EdStem's API is deeply nested. You likely need to dig into
        # data['lesson']['slides'] or data['lesson']['modules']
        # For now, we'll assume a flattened content field exists
        content_body = clean_html(str(data.get("lesson", {})))

        meta = generate_metadata_llm(content_body, target["title"])

        res.append(
            {
                "id": target["id"],
                "title": target["title"],
                "concepts": meta.get("concepts", []),
                "difficulty": meta.get("difficulty", "Unknown"),
                "url": target["url"],
            }
        )

    with open(OUTPUT_FILE, "w") as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    main()
