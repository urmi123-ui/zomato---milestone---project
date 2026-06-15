import pytest
from pydantic import ValidationError

from app.config import Settings
from app.services.llm_client import GroqClient, create_llm_client


def test_groq_client_requires_api_key() -> None:
    settings = Settings(_env_file=None, llm_provider="groq", llm_api_key="")
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        GroqClient(settings)


def test_create_llm_client_returns_groq_client() -> None:
    settings = Settings(_env_file=None, llm_provider="groq", llm_api_key="gsk_test")
    client = create_llm_client(settings)
    assert isinstance(client, GroqClient)


def test_create_llm_client_rejects_non_groq_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider="openai")  # type: ignore[arg-type]
