"""LLM provider abstraction.

Switch providers via LLM_PROVIDER env var. All providers must expose a single
async-callable `chat(messages, *, temperature, max_tokens) -> str` so the rest
of the app stays agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

import httpx

from src.config import settings


@dataclass
class Message:
    role: str
    content: str


class LLMProviderProtocol(Protocol):
    async def chat(
        self,
        messages: Iterable[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str: ...


class OpenAICompatibleProvider:
    """Works for any OpenAI-compatible /v1/chat/completions endpoint
    (Groq, OpenRouter, OpenAI itself, local llama.cpp servers, etc.)."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model

    async def chat(
        self,
        messages: Iterable[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        payload = {
            "model": self._model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]


def build_provider() -> LLMProviderProtocol:
    provider = settings.LLM_PROVIDER
    model = settings.LLM_MODEL
    if provider == "groq":
        return OpenAICompatibleProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
            model=model,
        )
    if provider == "openrouter":
        return OpenAICompatibleProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            model=model,
        )
    if provider == "openai":
        return OpenAICompatibleProvider(
            base_url="https://api.openai.com/v1",
            api_key=settings.OPENAI_API_KEY,
            model=model,
        )
    if provider == "gemini":
        # Gemini uses a different REST shape; implement when first needed.
        raise NotImplementedError("Gemini provider not implemented yet.")
    if provider == "ollama":
        return OpenAICompatibleProvider(
            base_url=f"{settings.OLLAMA_HOST}/v1",
            api_key="ollama",
            model=model,
        )
    raise ValueError(f"Unknown LLM provider: {provider}")


llm = build_provider()
