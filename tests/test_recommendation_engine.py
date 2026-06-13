import pytest

from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant
from app.services.llm_client import LLMRequestError
from app.services.recommendation_engine import RecommendationEngine


class FakeLLMClient:
    def __init__(self, response: str | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls += 1
        if self.error is not None:
            raise self.error
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        return self.response or ""


@pytest.fixture
def preferences() -> UserPreferences:
    return UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="North Indian",
        min_rating=4.0,
        top_k=2,
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
            cuisines=["north indian"],
            rating=4.2,
            estimated_cost=700.0,
            budget_band="medium",
            metadata={"votes": 400},
        ),
    ]


class TestRecommendationEngine:
    def test_successful_llm_path(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        llm = FakeLLMClient(
            response="""
            {
              "summary": "Two strong options.",
              "recommendations": [
                {"restaurant_id": "r2", "rank": 1, "explanation": "Great fit for North Indian."},
                {"restaurant_id": "r1", "rank": 2, "explanation": "Higher rating alternative."}
              ]
            }
            """
        )
        engine = RecommendationEngine(llm_client=llm)
        response = engine.generate(preferences, candidates)

        assert response.meta["status"] == "success"
        assert response.meta["llm_fallback"] is False
        assert response.summary == "Two strong options."
        assert len(response.recommendations) == 2
        assert response.recommendations[0].restaurant.id == "r2"
        assert llm.calls == 1

    def test_fallback_on_invalid_json(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        llm = FakeLLMClient(response="Sorry, I cannot format JSON.")
        engine = RecommendationEngine(llm_client=llm)
        response = engine.generate(preferences, candidates)

        assert response.meta["status"] == "fallback"
        assert response.meta["llm_fallback"] is True
        assert len(response.recommendations) == 2
        assert response.recommendations[0].restaurant.name == "Alpha"

    def test_fallback_on_llm_error(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        llm = FakeLLMClient(error=LLMRequestError("timeout"))
        engine = RecommendationEngine(llm_client=llm)
        response = engine.generate(preferences, candidates)

        assert response.meta["llm_fallback"] is True
        assert len(response.recommendations) == 2

    def test_drops_hallucinated_ids(self, preferences: UserPreferences, candidates: list[Restaurant]) -> None:
        llm = FakeLLMClient(
            response="""
            {
              "recommendations": [
                {"restaurant_id": "fake", "rank": 1, "explanation": "Bad"},
                {"restaurant_id": "r1", "rank": 2, "explanation": "Good"}
              ]
            }
            """
        )
        engine = RecommendationEngine(llm_client=llm)
        response = engine.generate(preferences, candidates)

        assert response.meta["llm_fallback"] is False
        assert len(response.recommendations) == 2
        assert all(rec.restaurant.id in {"r1", "r2"} for rec in response.recommendations)

    def test_empty_candidates_returns_empty_response(self, preferences: UserPreferences) -> None:
        engine = RecommendationEngine(llm_client=FakeLLMClient())
        response = engine.generate(preferences, [])

        assert response.recommendations == []
        assert response.meta["status"] == "empty"
