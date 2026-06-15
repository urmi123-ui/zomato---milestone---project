from __future__ import annotations

from app.models.recommendation import Recommendation
from app.models.restaurant import Restaurant


def restaurant_quality_key(restaurant: Restaurant) -> tuple[float, int, str, str]:
    votes = restaurant.metadata.get("votes")
    vote_count = votes if isinstance(votes, int) else 0
    return (
        -restaurant.rating,
        -vote_count,
        restaurant.name.lower(),
        restaurant.id,
    )


def deduplicate_restaurants_by_name(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Keep one restaurant per case-insensitive name (highest rating, then votes)."""
    best_by_name: dict[str, Restaurant] = {}
    for restaurant in restaurants:
        key = restaurant.name.strip().lower()
        if not key:
            continue
        existing = best_by_name.get(key)
        if existing is None or restaurant_quality_key(restaurant) < restaurant_quality_key(existing):
            best_by_name[key] = restaurant

    deduped = list(best_by_name.values())
    deduped.sort(key=restaurant_quality_key)
    return deduped


def deduplicate_recommendations_by_name(
    recommendations: list[Recommendation],
) -> list[Recommendation]:
    seen_names: set[str] = set()
    unique: list[Recommendation] = []
    for recommendation in recommendations:
        name_key = recommendation.restaurant.name.strip().lower()
        if not name_key or name_key in seen_names:
            continue
        seen_names.add(name_key)
        unique.append(recommendation)
    return unique
