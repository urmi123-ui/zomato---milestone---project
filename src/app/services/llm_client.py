from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Thin wrapper over the Groq hosted API."""

    @abstractmethod
    def complete(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError


class GroqClient(LLMClient):
    """Groq chat completions via OpenAI-compatible API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if settings.llm_provider != "groq":
            raise ValueError("GroqClient requires LLM_PROVIDER=groq")
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required for Groq provider")

    def complete(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.settings.llm_model,
            "messages": messages,
            "temperature": self.settings.llm_temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.settings.groq_base_url.rstrip('/')}/chat/completions"
        return _post_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            settings=self.settings,
            extract_content=_extract_chat_content,
        )


def create_llm_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or get_settings()
    if settings.llm_provider != "groq":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}. Only 'groq' is supported.")
    return GroqClient(settings)


def _post_with_retry(
    *,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    settings: Settings,
    extract_content,
) -> str:
    last_error: Exception | None = None
    attempts = settings.llm_max_retries + 1

    for attempt in range(attempts):
        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return extract_content(response.json())
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as exc:
            last_error = exc
            logger.warning("Groq request failed (attempt %d/%d): %s", attempt + 1, attempts, exc)
            if attempt >= settings.llm_max_retries:
                break

    assert last_error is not None
    raise LLMRequestError(str(last_error)) from last_error


def _extract_chat_content(payload: dict[str, Any]) -> str:
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMRequestError("Groq response missing message content") from exc


class LLMRequestError(Exception):
    """Raised when the Groq provider request fails after retries."""
