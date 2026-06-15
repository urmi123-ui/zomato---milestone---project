import pytest

from app.data.dedup import deduplicate_recommendations_by_name, deduplicate_restaurants_by_name
from app.models.recommendation import Recommendation
from app.models.restaurant import Restaurant


def _restaurant(
    restaurant_id: str,
    name: str,
    *,
    rating: float = 4.0,
    votes: int = 0,
) -> Restaurant:
    return Restaurant(
        id=restaurant_id,
        name=name,
        location="koramangala, bangalore",
        cuisines=["north indian"],
        rating=rating,
        estimated_cost=800.0,
        budget_band="medium",
        metadata={"votes": votes},
    )


class TestDeduplicateRestaurantsByName:
    def test_keeps_highest_rated_duplicate_name(self) -> None:
        restaurants = [
            _restaurant("r1", "Onesta", rating=4.1, votes=100),
            _restaurant("r2", "onesta", rating=4.6, votes=50),
            _restaurant("r3", "Beta", rating=4.0),
        ]

        deduped = deduplicate_restaurants_by_name(restaurants)

        assert len(deduped) == 2
        assert {entry.name.lower() for entry in deduped} == {"onesta", "beta"}
        assert deduped[0].id == "r2"

    def test_case_insensitive_name_match(self) -> None:
        restaurants = [
            _restaurant("r1", "Pizza Hut", rating=4.0),
            _restaurant("r2", "PIZZA HUT", rating=4.5),
        ]

        deduped = deduplicate_restaurants_by_name(restaurants)

        assert len(deduped) == 1
        assert deduped[0].id == "r2"


class TestDeduplicateRecommendationsByName:
    def test_keeps_first_occurrence_by_rank(self) -> None:
        recommendations = [
            Recommendation(
                restaurant=_restaurant("r1", "Onesta", rating=4.6),
                rank=1,
                explanation="Best",
            ),
            Recommendation(
                restaurant=_restaurant("r2", "onesta", rating=4.1),
                rank=2,
                explanation="Duplicate name",
            ),
            Recommendation(
                restaurant=_restaurant("r3", "Beta", rating=4.0),
                rank=3,
                explanation="Unique",
            ),
        ]

        deduped = deduplicate_recommendations_by_name(recommendations)

        assert len(deduped) == 2
        assert [entry.restaurant.id for entry in deduped] == ["r1", "r3"]
