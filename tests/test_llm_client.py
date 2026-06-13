import pytest

from app.config import Settings
from app.services.llm_client import OpenAIClient


def test_openai_client_requires_api_key() -> None:
    settings = Settings(llm_api_key="")
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        OpenAIClient(settings)
