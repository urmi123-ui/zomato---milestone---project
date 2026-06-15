import pytest


@pytest.fixture(autouse=True)
def groq_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests use Groq settings even when local .env specifies another provider."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "llama-3.3-70b-versatile")
