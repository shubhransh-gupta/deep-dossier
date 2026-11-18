# ⚡ Deep Dossier

[![Documentation](https://img.shields.io/badge/Documentation-Apple%20HIG%20Style-blue?style=for-the-badge&logo=vercel)](https://agent-docs-coral.vercel.app)
[![GitHub Stars](https://img.shields.io/github/stars/shubhransh-gupta/deep-dossier?style=for-the-badge&color=2997ff)](https://github.com/shubhransh-gupta/deep-dossier/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **📖 Live Documentation & Interactive FAQs:** [https://agent-docs-coral.vercel.app](https://agent-docs-coral.vercel.app)

<p align="center">
  <img src="assets/demo.svg" alt="Deep Dossier Live Terminal Demo" width="100%" />
</p>

An open-source autonomous multi-step research agent with **universal model support**.

Deep Dossier decomposes complex research prompts into targeted search plans, recursively crawls dozens of web pages and documents in parallel, resolves information gaps, and produces publication-grade Markdown and interactive HTML dossiers with verified in-text citations.

## 🌐 Universal Model Support (Bring Your Own Key)

Deep Dossier is model-agnostic. Choose your preferred AI provider or run completely local:

| Provider | Supported Models | Environment Variable |
| :--- | :--- | :--- |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro` | `export GEMINI_API_KEY="..."` |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022`, `claude-3-7-sonnet`, `claude-3-opus` | `export ANTHROPIC_API_KEY="..."` |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini` | `export OPENAI_API_KEY="..."` |
| **DeepSeek** | `deepseek-chat`, `deepseek-reasoner` | `export DEEPSEEK_API_KEY="..."` |
| **NVIDIA Nemotron** | `nvidia/nemotron-4-340b-instruct` | `export NVIDIA_API_KEY="..."` |
| **OpenRouter** | 200+ models across all frontier labs | `export OPENROUTER_API_KEY="..."` |
| **Local / Self-Hosted** | Ollama (`llama3.2`, `mistral`, `qwen2.5`), vLLM | `--base-url http://localhost:11434/v1` |

## 🌟 Key Highlights

- **Multi-Provider Flexibility**: Switch between Gemini, Claude, GPT, DeepSeek, or local Ollama with a single flag.
- **Recursive Search & Discovery**: Explores multi-hop questions by identifying knowledge gaps after each crawl iteration.
- **Zero-Config Search**: Built-in DuckDuckGo search integration requiring zero additional API keys.
- **Publication Deliverables**: Exports structured Markdown, JSON intelligence dossiers, and self-contained dark-mode interactive HTML reports.

## 🚀 Quick Start

### 1. Installation

Install directly from PyPI:

```bash
pip install deep-dossier
```

Or install from source:

```bash
git clone https://github.com/shubhransh-gupta/deep-dossier.git
cd deep-dossier
pip install -e .
```

## ⚡ How to Use in Any Other Project (GitHub Action CI/CD)

You can drop **Deep Dossier** directly into **any GitHub repository** to automate recurring market research, competitive analysis, or technical investigations.

Available on the **GitHub Marketplace**: [`shubhransh-gupta/deep-dossier@v1`](https://github.com/shubhransh-gupta/deep-dossier)

### 1. Configure Your AI Provider Secret
In your target repository:
1. Navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Name the secret `GEMINI_API_KEY` (or `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`) and paste your API key.

### 2. Create the Workflow File
Add a new workflow file at `.github/workflows/deep-research.yml`:

```yaml
name: Automated Deep Research

on:
  workflow_dispatch:
    inputs:
      topic:
        description: 'Topic or investigative question to research'
        required: true
        default: 'Latest developments in frontier AI reasoning architectures'
      depth:
        description: 'Recursive search depth (1-3)'
        required: false
        default: '2'
  schedule:
    # Optional: Run automatically every Monday at 09:00 UTC
    - cron: '0 9 * * 1'

jobs:
  research:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Run Deep Dossier
        uses: shubhransh-gupta/deep-dossier@v1
        with:
          topic: ${{ inputs.topic || 'Weekly frontier AI industry research' }}
          api-key: ${{ secrets.GEMINI_API_KEY }}
          provider: 'gemini'
          depth: ${{ inputs.depth || '2' }}
          output-dir: './research_outputs'

      - name: Upload Research Dossier Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: research-dossier
          path: ./research_outputs/
```

### Action Inputs Reference

| Input | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `topic` | **Yes** | &mdash; | Research topic or query to investigate |
| `api-key` | **Yes** | &mdash; | AI provider API key (pass via `${{ secrets.GEMINI_API_KEY }}`) |
| `provider` | No | `gemini` | `gemini`, `anthropic`, `openai`, `deepseek` |
| `model` | No | Auto | Specific model override (e.g. `gemini-3-flash-preview`, `claude-3-5-sonnet`) |
| `depth` | No | `2` | Recursive crawl iterations (1 to 3) |
| `breadth` | No | `4` | Number of web sources crawled per iteration |
| `output-dir`| No | `./research_outputs` | Destination directory for `.md` and `.html` dossiers |

### 2. Set Your Preferred API Key

Choose any provider:
```bash
# Option A: Google Gemini
export GEMINI_API_KEY="AIzaSy..."

# Option B: Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Option C: OpenAI
export OPENAI_API_KEY="sk-proj-..."

# Option D: DeepSeek
export DEEPSEEK_API_KEY="sk-..."
```

### 3. Run a Research Mission

Using default/auto-detected provider:
```bash
deep-dossier "Analyze battery degradation patterns of LFP vs NMC cells in commercial EVs"
```

Explicitly choose provider and model:
```bash
# Using Anthropic Claude 3.5 Sonnet
deep-dossier "Solid-state battery commercial readiness" --provider anthropic --model claude-3-5-sonnet-20241022

# Using OpenAI GPT-4o
deep-dossier "Cross-border payment rail comparison" --provider openai --model gpt-4o

# Using Local Ollama
deep-dossier "Local AI agent architectures" --base-url http://localhost:11434/v1 --model llama3.2
```

## ⚙️ Options

```bash
deep-dossier [TOPIC] [OPTIONS]

Options:
  --provider, -p TEXT     LLM provider: gemini, openai, anthropic, deepseek, nvidia, ollama, openrouter
  --model, -m TEXT        Specific model name
  --base-url TEXT         Custom API base URL (for Ollama, vLLM, or custom proxies)
  --depth, -d INTEGER     Recursive search depth (default: 2)
  --breadth, -b INTEGER   Number of sources to retrieve per search query (default: 4)
  --output, -o PATH       Output directory for generated dossiers (default: ./research_outputs)
  --api-key, -k TEXT      Explicit API key override
  --no-html               Disable HTML report generation
```

## 📦 Project Structure

```
deep-dossier/
├── deep_dossier/
│   ├── agent.py       # Core autonomous orchestrator and synthesis engine
│   ├── llm.py         # Universal multi-provider LLM interface (Gemini/Claude/GPT/Ollama)
│   ├── crawler.py     # Concurrent HTML & document content extractor
│   ├── search.py      # Search engine interface
│   ├── report.py      # Markdown and interactive HTML renderer
│   ├── config.py      # Configuration and environment loader
│   └── cli.py         # Rich terminal interface
└── pyproject.toml     # Build metadata and entry points
```

## 📄 License

MIT License. Copyright (c) 2026 Shubhransh Gupta.
