from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.data.repository import RestaurantRepository
from app.models.filter import FilterCriteria, FilterResult
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class FilterService:
    """Apply deterministic filters and return a capped, pre-sorted candidate list."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def filter(
        self,
        preferences: UserPreferences,
        repository: RestaurantRepository,
    ) -> FilterResult:
        repository.ensure_loaded()
        criteria = self._to_criteria(preferences)
        matched = repository.filter(criteria)
        total_before_cap = len(matched)
        sorted_matches = sorted(matched, key=_candidate_sort_key)
        max_candidates = self.settings.max_candidates
        candidates = sorted_matches[:max_candidates]

        result = FilterResult(
            candidates=candidates,
            total_before_cap=total_before_cap,
            applied_filters=_build_applied_filters(preferences),
        )

        logger.info(
            "Filter matched %d restaurants; returning %d candidates (cap=%d)",
            total_before_cap,
            len(candidates),
            max_candidates,
        )
        return result

    @staticmethod
    def _to_criteria(preferences: UserPreferences) -> FilterCriteria:
        return FilterCriteria(
            location=preferences.location,
            budget=preferences.budget,
            cuisine=preferences.cuisine,
            min_rating=preferences.min_rating,
            additional_preferences=preferences.additional_preferences,
        )


def _candidate_sort_key(restaurant: Restaurant) -> tuple[float, int, str, str]:
    votes = restaurant.metadata.get("votes")
    vote_count = votes if isinstance(votes, int) else 0
    return (
        -restaurant.rating,
        -vote_count,
        restaurant.name.lower(),
        restaurant.id,
    )


def _build_applied_filters(preferences: UserPreferences) -> dict[str, str | float]:
    # additional_preferences is forwarded to the LLM only, not a hard filter.
    return {
        "location": preferences.location,
        "budget": preferences.budget,
        "cuisine": preferences.cuisine,
        "min_rating": preferences.min_rating,
    }
