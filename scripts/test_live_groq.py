#!/usr/bin/env python3
"""One-shot live Groq connectivity test. Run: PYTHONPATH=src python scripts/test_live_groq.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.config import Settings, get_settings
from app.models.preferences import UserPreferences
from app.services.orchestrator import RecommendationOrchestrator


def main() -> int:
    get_settings.cache_clear()
    settings = Settings()

    if not settings.llm_api_key:
        print("FAIL: No API key found. Set LLM_API_KEY (or GROQ_API_KEY) in .env and save the file.")
        return 1

    if not settings.llm_api_key.startswith("gsk_"):
        print("FAIL: Groq API keys start with 'gsk_'. Get one at https://console.groq.com")
        print(f"Your key prefix looks like: {settings.llm_api_key[:4]}...")
        return 1

    print(f"Provider: {settings.llm_provider} | Model: {settings.llm_model}")
    print("Calling Groq through full orchestrator pipeline...\n")

    preferences = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="North Indian",
        min_rating=4.0,
        top_k=2,
    )

    try:
        response = RecommendationOrchestrator(settings=settings).execute(
            preferences,
            correlation_id="live-groq-test",
        )
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 1

    print(f"Status: {response.meta.get('status')}")
    print(f"LLM fallback used: {response.meta.get('llm_fallback')}")
    print(f"Filter matched: {response.meta.get('candidates_considered')}")
    print(f"Groq latency: {response.meta.get('llm_latency_ms')} ms")
    print(f"Recommendations: {len(response.recommendations)}")

    if response.meta.get("llm_fallback"):
        print("\nFAIL: Groq did not return valid JSON (rating fallback was used). Check key/model.")
        return 2

    if not response.recommendations:
        print("\nNo matches for test preferences.")
        return 3

    top = response.recommendations[0]
    print(f"\nTop pick: #{top.rank} {top.restaurant.name} (★ {top.restaurant.rating})")
    print(f"Explanation: {top.explanation[:300]}")
    print("\nSUCCESS: Live Groq LLM call is working.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
