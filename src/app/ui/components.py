from __future__ import annotations

from typing import Literal

from pydantic import ValidationError

from app.models.preferences import UserPreferences


def format_cost(estimated_cost: float | None) -> str:
    if estimated_cost is None:
        return "N/A"
    return f"₹{estimated_cost:,.0f} for two"


def format_cuisines(cuisines: list[str]) -> str:
    if not cuisines:
        return "N/A"
    return ", ".join(c.title() for c in cuisines)


def build_preferences(
    *,
    location: str,
    budget: Literal["low", "medium", "high"],
    cuisine: str,
    min_rating: float,
    additional_preferences: str | None,
    top_k: int,
) -> UserPreferences:
    return UserPreferences(
        location=location.strip(),
        budget=budget,
        cuisine=cuisine.strip(),
        min_rating=min_rating,
        additional_preferences=additional_preferences.strip() if additional_preferences else None,
        top_k=top_k,
    )


def validate_form_inputs(location: str, cuisine: str) -> str | None:
    if not location.strip():
        return "Location is required."
    if not cuisine.strip():
        return "Cuisine is required."
    return None


def parse_preferences_safe(**kwargs) -> tuple[UserPreferences | None, str | None]:
    try:
        return build_preferences(**kwargs), None
    except ValidationError as exc:
        message = exc.errors()[0]["msg"] if exc.errors() else "Invalid preferences."
        return None, message
