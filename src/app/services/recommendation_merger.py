from __future__ import annotations

import logging

from app.data.dedup import deduplicate_recommendations_by_name, deduplicate_restaurants_by_name
from app.models.llm import ParsedLLMResponse
from app.models.preferences import UserPreferences
from app.models.recommendation import Recommendation
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class RecommendationMerger:
    """Join parsed LLM output with restaurant entities."""

    def merge(
        self,
        parsed: ParsedLLMResponse,
        candidates: list[Restaurant],
        preferences: UserPreferences,
    ) -> tuple[str | None, list[Recommendation]]:
        candidates_by_id = {candidate.id: candidate for candidate in candidates}
        recommendations: list[Recommendation] = []

        for item in parsed.recommendations:
            restaurant = candidates_by_id.get(item.restaurant_id)
            if restaurant is None:
                continue
            recommendations.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=item.rank,
                    explanation=item.explanation or _generic_explanation(preferences, restaurant),
                )
            )

        recommendations = self._finalize_recommendations(recommendations, candidates, preferences)
        return parsed.summary, recommendations

    def build_fallback(
        self,
        candidates: list[Restaurant],
        preferences: UserPreferences,
    ) -> tuple[str | None, list[Recommendation]]:
        logger.info("Using rating-based fallback recommendations")
        unique_candidates = deduplicate_restaurants_by_name(candidates)
        recommendations = self._finalize_recommendations([], unique_candidates, preferences)
        summary = (
            f"Showing top {len(recommendations)} rated matches for "
            f"{preferences.cuisine} in {preferences.location} within a {preferences.budget} budget."
        )
        return summary, recommendations

    def _finalize_recommendations(
        self,
        recommendations: list[Recommendation],
        candidates: list[Restaurant],
        preferences: UserPreferences,
    ) -> list[Recommendation]:
        recommendations = deduplicate_recommendations_by_name(recommendations)
        recommendations = self._backfill(recommendations, candidates, preferences)
        recommendations = deduplicate_recommendations_by_name(recommendations)
        recommendations = recommendations[: preferences.top_k]
        for index, recommendation in enumerate(recommendations, start=1):
            recommendation.rank = index
        return recommendations

    def _backfill(
        self,
        recommendations: list[Recommendation],
        candidates: list[Restaurant],
        preferences: UserPreferences,
    ) -> list[Recommendation]:
        if len(recommendations) >= preferences.top_k:
            return recommendations

        used_ids = {entry.restaurant.id for entry in recommendations}
        used_names = {entry.restaurant.name.strip().lower() for entry in recommendations}
        remaining = [
            candidate
            for candidate in candidates
            if candidate.id not in used_ids and candidate.name.strip().lower() not in used_names
        ]
        remaining = deduplicate_restaurants_by_name(remaining)
        remaining.sort(
            key=lambda restaurant: (
                -restaurant.rating,
                -(restaurant.metadata.get("votes") or 0)
                if isinstance(restaurant.metadata.get("votes"), int)
                else 0,
                restaurant.name.lower(),
                restaurant.id,
            )
        )

        next_rank = len(recommendations) + 1
        for restaurant in remaining:
            if len(recommendations) >= preferences.top_k:
                break
            name_key = restaurant.name.strip().lower()
            if name_key in used_names:
                continue
            recommendations.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=next_rank,
                    explanation=_generic_explanation(preferences, restaurant),
                )
            )
            used_ids.add(restaurant.id)
            used_names.add(name_key)
            next_rank += 1

        return recommendations


def _generic_explanation(preferences: UserPreferences, restaurant: Restaurant) -> str:
    cuisine_text = ", ".join(restaurant.cuisines) if restaurant.cuisines else preferences.cuisine
    return (
        f"Highly rated option in {restaurant.location} serving {cuisine_text}, "
        f"matching your {preferences.budget} budget and minimum rating of {preferences.min_rating}."
    )
