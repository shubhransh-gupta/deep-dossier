"""
Configuration settings and environment management for Open Deep Research.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List


def load_env_file(dotenv_path: Optional[str] = None):
    """Simple robust .env loader without requiring external heavy dependencies."""
    paths_to_check = [
        dotenv_path,
        Path.cwd() / ".env",
        Path.cwd() / ".env.local",
        Path.home() / ".config" / "open-deep-research" / ".env",
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


# Try loading from any nearby .env
load_env_file()


@dataclass
class ResearchConfig:
    """Config options for the Deep Research Agent."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    model: str = "gemini-2.5-flash"
    fallback_models: List[str] = field(default_factory=lambda: [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-4-hydrogen"
    ])
    max_depth: int = 2
    breadth: int = 4
    max_queries_per_step: int = 3
    max_sources_to_scrape: int = 15
    timeout_seconds: int = 15
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (OpenDeepResearch/0.1.0)"
    )
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "research_outputs")
    generate_html: bool = True
    generate_markdown: bool = True
    generate_json: bool = True
    verbose: bool = True

    def validate(self):
        """Validates that necessary configuration is present."""
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set.\n"
                "Please set it via environment variable: export GEMINI_API_KEY='your-key'\n"
                "Or pass it with --api-key in the CLI.\n"
                "Get a free Gemini API key at: https://aistudio.google.com/"
            )
