# Lumina: Intelligent Course Navigation for CSE 12x

**Lumina** is a RAG-based assistant designed to help University of Washington Computer Science students navigate section materials and practice problems with semantic precision.

```
╭───────────────────────────────────────────────────────────────╮
│ ✨ Lumina RAG Assistant ✨                                    │
│ Type your questions about CSE 122 below. Type 'exit' to quit. │
╰───────────────────────────────────────────────────────────────╯

>  I'm having trouble with stacks and queues...
                                                                         Recommended Practice                                                                         
 Problem                                                              Concepts                       Link                                                             
 ⭐Double Up - Stacks & Queues Edition [Complex Programming Problem]  stacks, queues, arrays         https://edstem.org/us/courses/90026/lessons/155022/slides/904432 
 ⭐From Counts [Complex Programming Problem]                          arrays, lists, stacks, queues  https://edstem.org/us/courses/90026/lessons/155015/slides/904375 

>  
```

---

## 🚀 Engineering Phases
### 1. Data Ingestion & Enrichment (The ETL Pipeline)

We successfully moved from unstructured, web-based course modules to a structured, LLM-enhanced knowledge base.

The "Hybrid" Extraction Strategy: Rather than building a brittle web scraper, we utilised a Stage-1 Console Extraction method. By executing JS snippets in the browser context, we bypassed complex React-based DOM rendering to generate a pristine `targets.json`.

Silver Labeling: During ingestion, we use a quantised Llama-3.2-1B model to "silver-label" raw HTML. The LLM automatically extracts core concepts (e.g., "Reference Semantics") and assesses relative difficulty for smarter ranking.

### 2. Neural Retrieval & TUI (The Search Engine)

We implemented a semantic retrieval layer to bridge the gap between student queries and curriculum data.

Neural Vector Embeddings: Lumina uses a Bi-Encoder architecture (all-MiniLM-L6-v2) to map course problems into a 384-dimensional vector space.

Semantic Mapping: Problems are indexed by a composite key of Title + Concept Tags. We utilise Cosine Similarity to retrieve contextually relevant problems even when student terminology doesn't perfectly match the curriculum.

Terminal UI (TUI): Built with Rich, the interface masks inference latency and provides formatted, actionable tables for the student.

---

## 💭 Project Methodology & Decisions

### 1. Reproducible Environment (NixOS + uv)
To ensure the system runs identically on any machine, Lumina uses a **Nix flake** to manage the system-level dependencies (Python interpreter, C++ libraries for inference). 
- **Package Management:** We utilise `uv` for lightning-fast Python dependency management.
- **Architecture Choice:** This "Layered" approach ensures that low-level binaries for AI inference are correctly linked on NixOS while maintaining a standard developer experience.

### 2. Local-First AI Inference (Llama-cpp)
Lumina prioritises **data privacy** and **system autonomy**. 
- **FERPA-Compliant:** By eliminating third-party API dependencies, all student-AI interactions remain on-device. This mitigates PII (Personally Identifiable Information) leakage risks and maintains data sovereignty.

---

## 📂 System Architecture
```
lumina/
├── flake.nix             # System-level reproducibility
├── pyproject.toml        # uv dependency management
├── src/
│   └── app.py            # Lumina app
├── data/
│   ├── sections.json     # Stage 1: Sections containing problemsets
│   └── schema.json       # Stage 2: LLM-enhanced knowledge base
├── models/
│   └── Llama-3.2-1B-Instruct-Q4_K_M.gguf # Quantised local weights
└── scripts/
    ├── extract.js        # Aggregates problemset links via browser console
    └── scrape.py         # Scrapes problems to collect metadata
```

---

## 🛠️ Installation & Usage

```bash
# enter the reproducible shell
nix develop

# run the lumina assistant!
just app
```
