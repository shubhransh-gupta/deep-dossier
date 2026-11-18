"""
Unified multi-provider LLM interface supporting Gemini, OpenAI, Anthropic, DeepSeek, Nemotron, and Ollama.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
import requests

logger = logging.getLogger(__name__)


class UnifiedLLM:
    """
    Universal LLM client that routes requests to:
    - Google Gemini
    - OpenAI (GPT-4o, o1, o3-mini, etc.)
    - Anthropic (Claude 3.5 Sonnet, Claude 3.7 Sonnet, etc.)
    - OpenAI-Compatible endpoints (OpenRouter, DeepSeek, NVIDIA Nemotron, Ollama, vLLM)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.provider, self.model = self._resolve_provider_and_model(provider, model)
        self._resolve_api_key()

    def _resolve_provider_and_model(self, provider: Optional[str], model: Optional[str]) -> tuple:
        """Auto-detect provider based on model name or available environment variables."""
        if provider:
            p = provider.lower()
            m = model or self._default_model_for_provider(p)
            return p, m

        m = (model or "").lower()
        if "claude" in m:
            return "anthropic", model
        if any(x in m for x in ["gpt", "o1", "o3", "chatgpt"]):
            return "openai", model
        if "gemini" in m:
            return "gemini", model
        if "deepseek" in m:
            return "deepseek", model
        if "nemotron" in m or "nvidia" in m:
            return "nvidia", model

        # Check environment variable presence
        if os.getenv("GEMINI_API_KEY"):
            return "gemini", model or "gemini-2.5-flash"
        if os.getenv("OPENAI_API_KEY"):
            return "openai", model or "gpt-4o"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic", model or "claude-3-5-sonnet-20241022"
        if os.getenv("OPENROUTER_API_KEY"):
            return "openrouter", model or "meta-llama/llama-3.3-70b-instruct"
        if os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek", model or "deepseek-chat"

        return "gemini", model or "gemini-2.5-flash"

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "gemini": "gemini-2.5-flash",
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "openrouter": "meta-llama/llama-3.3-70b-instruct",
            "deepseek": "deepseek-chat",
            "nvidia": "nvidia/nemotron-4-340b-instruct",
            "ollama": "llama3.2",
        }
        return defaults.get(provider, "gemini-2.5-flash")

    def _resolve_api_key(self):
        if self.api_key:
            return

        key_map = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
        }
        env_var = key_map.get(self.provider)
        if env_var:
            self.api_key = os.getenv(env_var)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Dispatch generation to appropriate provider implementation."""
        if self.provider == "gemini":
            return self._call_gemini(prompt, system_instruction)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, system_instruction)
        elif self.provider in ("openai", "openrouter", "deepseek", "nvidia", "ollama") or self.base_url:
            return self._call_openai_compatible(prompt, system_instruction)
        else:
            return self._call_gemini(prompt, system_instruction)

    def _call_gemini(self, prompt: str, system_instruction: Optional[str]) -> str:
        # Try google-genai SDK first
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key)
            cfg = {}
            if system_instruction:
                cfg["system_instruction"] = system_instruction
            res = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(**cfg) if cfg else None
            )
            if res and res.text:
                return res.text
        except Exception:
            pass

        # Fallback to direct REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM: {system_instruction}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        resp = requests.post(url, json={"contents": contents}, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_anthropic(self, prompt: str, system_instruction: Optional[str]) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_instruction:
            payload["system"] = system_instruction

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content", [])
        if content and "text" in content[0]:
            return content[0]["text"]
        return ""

    def _call_openai_compatible(self, prompt: str, system_instruction: Optional[str]) -> str:
        endpoint_map = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
            "ollama": "http://localhost:11434/v1/chat/completions",
        }
        url = self.base_url or endpoint_map.get(self.provider, "https://api.openai.com/v1/chat/completions")
        headers = {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
