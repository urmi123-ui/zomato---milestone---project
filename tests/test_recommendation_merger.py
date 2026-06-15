import pytest

from app.models.llm import LLMRecommendationItem, ParsedLLMResponse
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant
from app.services.recommendation_merger import RecommendationMerger


@pytest.fixture
def preferences() -> UserPreferences:
    return UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="North Indian",
        min_rating=4.0,
        top_k=3,
    )


@pytest.fixture
def candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Alpha",
            location="banashankari, bangalore",
            cuisines=["north indian"],
            rating=4.5,
            estimated_cost=800.0,
            budget_band="medium",
            metadata={"votes": 900},
        ),
        Restaurant(
            id="r2",
            name="Beta",
            location="banashankari, bangalore",
            cuisines=["north indian", "chinese"],
            rating=4.3,
            estimated_cost=700.0,
            budget_band="medium",
            metadata={"votes": 500},
        ),
        Restaurant(
            id="r3",
            name="Gamma",
            location="banashankari, bangalore",
            cuisines=["north indian"],
            rating=4.1,
            estimated_cost=600.0,
            budget_band="medium",
            metadata={"votes": 300},
        ),
        Restaurant(
            id="r4",
            name="Delta",
            location="banashankari, bangalore",
            cuisines=["north indian"],
            rating=4.0,
            estimated_cost=650.0,
            budget_band="medium",
            metadata={"votes": 200},
        ),
    ]


class TestRecommendationMerger:
    def test_merge_joins_restaurants_by_id(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> None:
        parsed = ParsedLLMResponse(
            summary="Top picks",
            recommendations=[
                LLMRecommendationItem(restaurant_id="r2", rank=1, explanation="Best match"),
                LLMRecommendationItem(restaurant_id="r1", rank=2, explanation="Runner up"),
            ],
        )
        summary, recommendations = RecommendationMerger().merge(parsed, candidates, preferences)

        assert summary == "Top picks"
        assert len(recommendations) == 3  # backfills to top_k=3
        assert recommendations[0].restaurant.name == "Beta"
        assert recommendations[0].explanation == "Best match"
        assert recommendations[1].restaurant.name == "Alpha"

    def test_backfills_to_top_k(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        parsed = ParsedLLMResponse(
            recommendations=[
                LLMRecommendationItem(restaurant_id="r1", rank=1, explanation="Only one from LLM"),
            ]
        )
        _, recommendations = RecommendationMerger().merge(parsed, candidates, preferences)

        assert len(recommendations) == 3
        assert {entry.restaurant.id for entry in recommendations} == {"r1", "r2", "r3"}

    def test_fallback_ranks_by_rating(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        summary, recommendations = RecommendationMerger().build_fallback(candidates, preferences)

        assert summary is not None
        assert len(recommendations) == 3
        assert recommendations[0].restaurant.name == "Alpha"
        assert recommendations[0].rank == 1
        assert "budget" in recommendations[0].explanation.lower()

    def test_merge_deduplicates_duplicate_names(self, preferences: UserPreferences) -> None:
        candidates = [
            Restaurant(
                id="r1",
                name="Onesta",
                location="koramangala, bangalore",
                cuisines=["north indian"],
                rating=4.6,
                budget_band="medium",
            ),
            Restaurant(
                id="r2",
                name="onesta",
                location="koramangala 5th block, bangalore",
                cuisines=["north indian"],
                rating=4.2,
                budget_band="medium",
            ),
            Restaurant(
                id="r3",
                name="Beta",
                location="koramangala, bangalore",
                cuisines=["north indian"],
                rating=4.4,
                budget_band="medium",
            ),
            Restaurant(
                id="r4",
                name="Gamma",
                location="koramangala, bangalore",
                cuisines=["north indian"],
                rating=4.1,
                budget_band="medium",
            ),
        ]
        parsed = ParsedLLMResponse(
            recommendations=[
                LLMRecommendationItem(restaurant_id="r1", rank=1, explanation="First Onesta"),
                LLMRecommendationItem(restaurant_id="r2", rank=2, explanation="Second Onesta"),
                LLMRecommendationItem(restaurant_id="r3", rank=3, explanation="Beta"),
            ]
        )

        _, recommendations = RecommendationMerger().merge(parsed, candidates, preferences)

        names = [entry.restaurant.name.lower() for entry in recommendations]
        assert len(names) == len(set(names))
        assert names.count("onesta") == 1
