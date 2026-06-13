import json

import pytest

from app.config import Settings
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant
from app.services.prompt_builder import PromptBuilder
from app.services.prompt_templates import PROMPT_VERSION, SYSTEM_PROMPT


@pytest.fixture
def settings() -> Settings:
    return Settings(max_additional_preferences_length=500)


@pytest.fixture
def preferences() -> UserPreferences:
    return UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="North Indian",
        min_rating=4.0,
        additional_preferences="family-friendly, quick service",
        top_k=3,
    )


@pytest.fixture
def candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="abc123",
            name="Jalsa",
            location="banashankari, bangalore",
            cuisines=["north indian", "mughlai"],
            rating=4.1,
            estimated_cost=800.0,
            budget_band="medium",
        ),
        Restaurant(
            id="def456",
            name="Spice Elephant",
            location="banashankari, bangalore",
            cuisines=["chinese", "north indian"],
            rating=4.5,
            estimated_cost=800.0,
            budget_band="medium",
        ),
    ]


class TestPromptBuilder:
    def test_build_returns_system_and_user_messages(
        self,
        settings: Settings,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> None:
        builder = PromptBuilder(settings=settings)
        messages = builder.build(preferences, candidates)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[0]["content"] == SYSTEM_PROMPT

    def test_user_message_contains_preferences_candidates_and_schema(
        self,
        settings: Settings,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> None:
        builder = PromptBuilder(settings=settings)
        user_content = builder.build(preferences, candidates)[1]["content"]

        assert PROMPT_VERSION in user_content
        assert "Bangalore" in user_content
        assert "family-friendly, quick service" in user_content
        assert "abc123" in user_content
        assert "def456" in user_content
        assert '"top_k": 3' in user_content
        assert "restaurant_id" in user_content
        assert "Return JSON matching this schema exactly" in user_content

    def test_truncates_long_additional_preferences(self, settings: Settings, candidates: list[Restaurant]) -> None:
        long_text = "x" * 700
        preferences = UserPreferences(
            location="Bangalore",
            budget="medium",
            cuisine="Indian",
            min_rating=4.0,
            additional_preferences=long_text,
        )
        user_content = PromptBuilder(settings=settings).build(preferences, candidates)[1]["content"]
        assert "..." in user_content
        assert long_text not in user_content

    def test_candidate_payload_is_minimal_json(
        self,
        settings: Settings,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> None:
        user_content = PromptBuilder(settings=settings).build(preferences, candidates)[1]["content"]
        candidate_section = user_content.split("Candidate restaurants (choose ONLY from this list):\n", 1)[1]
        candidate_json = candidate_section.split("\n\nTask:", 1)[0]
        rows = json.loads(candidate_json)

        assert len(rows) == 2
        assert set(rows[0].keys()) == {
            "restaurant_id",
            "name",
            "location",
            "cuisines",
            "rating",
            "estimated_cost",
            "budget_band",
        }
