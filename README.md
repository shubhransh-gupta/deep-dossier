# ⚡ Deep Dossier

An open-source autonomous multi-step research agent powered by Google Gemini.

Deep Dossier decomposes complex research prompts into targeted search plans, recursively crawls dozens of web pages and documents in parallel, resolves information gaps, and produces publication-grade Markdown and interactive HTML dossiers with verified in-text citations.

## 🌟 Key Highlights

- **1M+ Token Context Ingestion**: Leverages Gemini's vast context window to analyze complete documents, whitepapers, and articles without chunking loss.
- **Recursive Search & Discovery**: Explores multi-hop questions by identifying knowledge gaps after each crawl iteration.
- **Zero-Config Search**: Comes with built-in DuckDuckGo search integration requiring zero additional API keys.
- **Publication Deliverables**: Exports structured Markdown, JSON intelligence dossiers, and self-contained dark-mode interactive HTML reports.

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/shubhransh-gupta/deep-dossier.git
cd deep-dossier
pip install -e .
```

### 2. Configure Gemini API Key

Obtain a key from [Google AI Studio](https://aistudio.google.com/):

```bash
export GEMINI_API_KEY="AIzaSy..."
```

### 3. Run a Research Mission

```bash
deep-dossier "Analyze battery degradation patterns of LFP vs NMC cells in commercial EVs"
```

Or run interactively:
```bash
deep-dossier
```

## ⚙️ Options

```bash
deep-dossier [TOPIC] [OPTIONS]

Options:
  --depth, -d INTEGER     Recursive search depth (default: 2)
  --breadth, -b INTEGER   Number of sources to retrieve per search query (default: 4)
  --model, -m TEXT        Gemini model identifier (default: gemini-2.5-flash)
  --output, -o PATH       Output directory for generated dossiers (default: ./research_outputs)
  --api-key, -k TEXT      Explicit Gemini API key override
  --no-html               Disable HTML report generation
```

## 📦 Project Structure

```
deep-dossier/
├── deep_dossier/
│   ├── agent.py       # Core autonomous orchestrator and synthesis engine
│   ├── crawler.py     # Concurrent HTML & document content extractor
│   ├── search.py      # Search engine interface
│   ├── report.py      # Markdown and interactive HTML renderer
│   ├── config.py      # Configuration and environment loader
│   └── cli.py         # Rich terminal interface
└── pyproject.toml     # Build metadata and entry points
```

## 📄 License

MIT License. Copyright (c) 2026 Shubhransh Gupta.
