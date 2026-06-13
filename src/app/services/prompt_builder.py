from __future__ import annotations

import json
from typing import Any

from app.config import Settings, get_settings
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant
from app.services.prompt_templates import OUTPUT_SCHEMA, PROMPT_VERSION, SYSTEM_PROMPT


class PromptBuilder:
    """Build LLM messages from user preferences and filtered candidates."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build(self, preferences: UserPreferences, candidates: list[Restaurant]) -> list[dict[str, str]]:
        allowed_ids = [candidate.id for candidate in candidates]
        user_content = self._build_user_content(preferences, candidates, allowed_ids)
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def _build_user_content(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        allowed_ids: list[str],
    ) -> str:
        preference_block = self._serialize_preferences(preferences)
        candidate_block = self._serialize_candidates(candidates)

        return (
            f"Prompt version: {PROMPT_VERSION}\n\n"
            f"User preferences:\n{preference_block}\n\n"
            f"Allowed restaurant_id values:\n{json.dumps(allowed_ids)}\n\n"
            f"Candidate restaurants (choose ONLY from this list):\n{candidate_block}\n\n"
            f"Task:\n"
            f"- Rank the top {preferences.top_k} restaurants for this user.\n"
            f"- Provide a concise explanation for each ranked restaurant.\n"
            f"- Include an optional one-paragraph summary of the overall selection.\n"
            f"- Use only restaurant_id values from the allowed list.\n\n"
            f"Return JSON matching this schema exactly:\n{OUTPUT_SCHEMA}"
        )

    def _serialize_preferences(self, preferences: UserPreferences) -> str:
        additional = preferences.additional_preferences
        if additional and len(additional) > self.settings.max_additional_preferences_length:
            additional = additional[: self.settings.max_additional_preferences_length] + "..."

        payload = {
            "location": preferences.location,
            "budget": preferences.budget,
            "cuisine": preferences.cuisine,
            "min_rating": preferences.min_rating,
            "additional_preferences": additional or "none specified",
            "top_k": preferences.top_k,
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def _serialize_candidates(candidates: list[Restaurant]) -> str:
        rows: list[dict[str, Any]] = []
        for candidate in candidates:
            rows.append(
                {
                    "restaurant_id": candidate.id,
                    "name": candidate.name,
                    "location": candidate.location,
                    "cuisines": candidate.cuisines,
                    "rating": candidate.rating,
                    "estimated_cost": candidate.estimated_cost,
                    "budget_band": candidate.budget_band,
                }
            )
        return json.dumps(rows, indent=2)
