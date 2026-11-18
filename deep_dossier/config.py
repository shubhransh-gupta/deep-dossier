"""
Configuration settings and environment management for Deep Dossier.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List


def load_env_file(dotenv_path: Optional[str] = None):
    """Simple robust .env loader."""
    paths_to_check = [
        dotenv_path,
        Path.cwd() / ".env",
        Path.cwd() / ".env.local",
        Path.home() / ".config" / "deep-dossier" / ".env",
    ]
    for p in paths_to_check:
        if p and Path(p).is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
                break
            except Exception:
                pass


load_env_file()


@dataclass
class ResearchConfig:
    """Config options for the Deep Dossier Agent supporting multiple LLM providers."""
    provider: Optional[str] = None  # 'gemini', 'openai', 'anthropic', 'deepseek', 'nvidia', 'ollama', 'openrouter'
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_depth: int = 2
    breadth: int = 4
    max_queries_per_step: int = 3
    max_sources_to_scrape: int = 15
    timeout_seconds: int = 20
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (DeepDossier/0.1.0)"
    )
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "research_outputs")
    generate_html: bool = True
    generate_markdown: bool = True
    generate_json: bool = True
    verbose: bool = True

    def validate(self):
        """Validates that at least one provider key or base_url is accessible."""
        available_keys = [
            self.api_key,
            os.getenv("GEMINI_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENROUTER_API_KEY"),
            os.getenv("DEEPSEEK_API_KEY"),
            os.getenv("NVIDIA_API_KEY"),
            self.base_url,
        ]
        if not any(available_keys):
            raise ValueError(
                "No API Key found.\n"
                "Please set one of the following environment variables:\n"
                "  • export GEMINI_API_KEY='...'\n"
                "  • export OPENAI_API_KEY='...'\n"
                "  • export ANTHROPIC_API_KEY='...'\n"
                "  • export OPENROUTER_API_KEY='...'\n"
                "  • export DEEPSEEK_API_KEY='...'\n"
                "  • export NVIDIA_API_KEY='...'\n"
                "Or specify --api-key / --base-url (for local Ollama/vLLM)."
            )
