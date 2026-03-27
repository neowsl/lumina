# Lumina: Intelligent Course Navigation for CSE 12x

**Lumina** is a RAG-based assistant designed to help University of Washington Computer Science students navigate section materials, practice problems, and course slides with semantic precision.

## 🚀 Current Status: Engineering Phase 1 (Data Ingestion)
We have successfully implemented the "Lumina ETL Pipeline," moving from unstructured web-based course modules to a structured, LLM-enhanced knowledge base.

---

## 🛠 Project Methodology & Decisions

### 1. Reproducible Environment (NixOS + uv)
To ensure the system runs identically on any machine, Lumina uses a **Nix Flake** to manage the system-level dependencies (Python interpreter, C++ libraries for inference). 
* **Package Management:** We utilize `uv` for lightning-fast, lockfile-backed Python dependency management.
* **Architecture Choice:** This "Layered" approach ensures that low-level binaries for AI inference are correctly linked on NixOS while maintaining a standard developer experience.

### 2. The "Hybrid" Extraction Strategy
Rather than building a brittle, high-overhead web scraper, we utilized a **Stage-1 Console Extraction** method.
* **Technique:** JavaScript snippets executed in the browser context allowed us to bypass complex React-based DOM rendering and authentication barriers.
* **Output:** A pristine `targets.json` containing specific "Section" problem metadata and direct EdStem API endpoints.

### 3. Local-First AI Inference (Llama-cpp)
Lumina prioritizes **Data Privacy** and **System Autonomy**. 
* **The Decision:** We transitioned from daemon-based models (Ollama) to `llama-cpp-python` for direct control over the model lifecycle.
* **Silver Labeling:** During ingestion, we use a quantized **Llama-3-8B** model to "silver-label" raw HTML. The LLM automatically extracts:
    * **Core Concepts:** (e.g., "Reference Semantics", "File I/O")
    * **Relative Difficulty:** For smarter retrieval ranking.

---

## 📂 System Architecture
```
lumina/
├── flake.nix             # System-level reproducibility
├── pyproject.toml        # uv dependency management
├── data/
│   ├── sections.json     # Stage 1: Sections containing problemsets
│   └── schema.json       # Stage 2: LLM-enhanced knowledge base
├── models/
│   └── llama-3-8b.gguf   # Quantized local weights
└── scripts/
    ├── extract.js        # Aggregates problemset links via browser console
    └── scrape.py         # Scrapes problems to collect metadata
```
