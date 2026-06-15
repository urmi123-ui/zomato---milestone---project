from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.ui.components import (
    build_preferences,
    format_cost,
    format_cuisines,
    parse_preferences_safe,
    validate_form_inputs,
)


class TestUIComponents:
    def test_format_cost(self) -> None:
        assert format_cost(800.0) == "₹800 for two"
        assert format_cost(None) == "N/A"

    def test_format_cuisines(self) -> None:
        assert format_cuisines(["north indian", "chinese"]) == "North Indian, Chinese"
        assert format_cuisines([]) == "N/A"

    def test_build_preferences(self) -> None:
        prefs = build_preferences(
            location="Bangalore",
            budget="medium",
            cuisine="North Indian",
            min_rating=4.0,
            additional_preferences="family-friendly",
            top_k=3,
        )
        assert prefs.location == "Bangalore"
        assert prefs.top_k == 3

    def test_validate_form_inputs(self) -> None:
        assert validate_form_inputs("Bangalore", "Indian") is None
        assert validate_form_inputs("  ", "Indian") == "Location is required."
        assert validate_form_inputs("Bangalore", " ") == "Cuisine is required."

    def test_parse_preferences_safe_invalid_rating(self) -> None:
        prefs, error = parse_preferences_safe(
            location="Bangalore",
            budget="medium",
            cuisine="Indian",
            min_rating=6.0,
            additional_preferences=None,
            top_k=5,
        )
        assert prefs is None
        assert error is not None

    def test_build_preferences_rejects_empty_location(self) -> None:
        with pytest.raises(ValidationError):
            build_preferences(
                location="  ",
                budget="low",
                cuisine="Indian",
                min_rating=3.0,
                additional_preferences=None,
                top_k=5,
            )
