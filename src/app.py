import json
import sys
import time
from typing import Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sentence_transformers import SentenceTransformer, util

console = Console()


class LuminaEngine:
    def __init__(self, schema_path: str):
        self.schema_path = schema_path
        self.data = self._load_data()
        with console.status("[bold green]Waking up Lumina...[/bold green]"):
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.embeddings = self._index_problems()

    def _load_data(self) -> List[Dict]:
        try:
            with open(self.schema_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]ERROR: {self.schema_path} not found.[/red]")
            sys.exit(1)

    def _index_problems(self):
        descriptions = [
            f"{item['title']}: {' '.join(item['concepts'])}" for item in self.data
        ]
        return self.model.encode(descriptions, convert_to_tensor=True)

    def search(self, query: str, top_k: int = 2):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]
        return hits


def main():
    engine = LuminaEngine("data/schema.json")

    console.print(
        Panel.fit(
            "✨ [bold cyan]Lumina RAG Assistant[/bold cyan] ✨\n"
            "[italic]Type your questions about CSE 122 below. Type 'exit' to quit.[/italic]",
            border_style="blue",
        )
    )

    while True:
        try:
            query = console.input("\n[bold green]> [/bold green] ")

            if query.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye! Happy coding :)[/yellow]")
                break

            if not query.strip():
                continue

            with console.status("[bold blue]Scanning Section Problems..."):
                hits = engine.search(query)
                time.sleep(0.6)

            if not hits:
                console.print("[red]No relevant problems found.[/red]")
                continue

            table = Table(title="Recommended Practice", box=None)
            table.add_column("Problem", style="cyan", no_wrap=True)
            table.add_column("Concepts", style="magenta")
            table.add_column("Link", style="blue")

            for hit in hits:
                item = engine.data[hit["corpus_id"]]
                concepts = (
                    ", ".join(item["concepts"])
                    if item["concepts"]
                    else "General Review"
                )
                table.add_row(item["title"], concepts, item["url"])

            console.print(table)

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
