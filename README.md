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

```bash
git clone https://github.com/shubhransh-gupta/deep-dossier.git
cd deep-dossier
pip install -e .
```

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
