from pathlib import Path

import pytest

from app.config import Settings
from app.data.repository import RestaurantRepository
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.preprocessor import Preprocessor
from app.ingestion.writer import PersistenceWriter
from app.models.preferences import UserPreferences
from app.services.filter_service import FilterService
from app.services.orchestrator import RecommendationOrchestrator, StoreNotLoadedError
from app.services.recommendation_engine import RecommendationEngine
from tests.test_schema_normalizer import SAMPLE_HF_ROW


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls += 1
        return self.response


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_path=tmp_path / "restaurants.parquet",
        budget_low_max=500,
        budget_medium_max=1500,
        max_candidates=30,
        llm_provider="groq",
        llm_api_key="gsk_test",
    )


@pytest.fixture
def repository(settings: Settings) -> RestaurantRepository:
    normalizer = SchemaNormalizer(settings=settings)
    rows = [
        SAMPLE_HF_ROW,
        {
            **SAMPLE_HF_ROW,
            "name": "Spice Elephant",
            "rate": "4.5/5",
            "votes": 900,
            "cuisines": "Chinese, North Indian, Thai",
        },
        {
            **SAMPLE_HF_ROW,
            "name": "Delhi Darbar",
            "address": "123, Connaught Place, New Delhi",
            "location": "Connaught Place",
            "cuisines": "North Indian, Mughlai",
            "approx_cost(for two people)": "400",
            "rate": "4.5/5",
        },
    ]
    restaurants = Preprocessor().process(normalizer.normalize_batch(rows))
    PersistenceWriter(settings.data_path).write(restaurants)
    repo = RestaurantRepository(data_path=settings.data_path, settings=settings)
    repo.load()
    return repo


@pytest.fixture
def orchestrator(settings: Settings, repository: RestaurantRepository) -> RecommendationOrchestrator:
    llm = FakeLLMClient(
        response="""
        {
          "summary": "Strong North Indian picks in Bangalore.",
          "recommendations": [
            {
              "restaurant_id": "PLACEHOLDER",
              "rank": 1,
              "explanation": "Excellent North Indian menu within medium budget."
            }
          ]
        }
        """
    )
    engine = RecommendationEngine(settings=settings, llm_client=llm)
    return RecommendationOrchestrator(
        repository=repository,
        filter_service=FilterService(settings=settings),
        recommendation_engine=engine,
        settings=settings,
    )


class TestRecommendationOrchestrator:
    def test_execute_returns_full_response(
        self,
        orchestrator: RecommendationOrchestrator,
        repository: RestaurantRepository,
    ) -> None:
        first_id = repository.get_all()[0].id
        engine = orchestrator.recommendation_engine
        assert isinstance(engine.llm_client, FakeLLMClient)
        engine.llm_client.response = engine.llm_client.response.replace("PLACEHOLDER", first_id)

        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="north indian",
            min_rating=4.0,
            top_k=2,
        )
        response = orchestrator.execute(preferences, correlation_id="test-123")

        assert response.meta["correlation_id"] == "test-123"
        assert response.meta["candidates_considered"] >= 1
        assert response.meta["filters_applied"]["location"] == "bangalore"
        assert response.meta["llm_provider"] == "groq"
        assert "llm_latency_ms" in response.meta
        assert len(response.recommendations) >= 1

    def test_empty_filter_skips_llm(
        self,
        orchestrator: RecommendationOrchestrator,
    ) -> None:
        preferences = UserPreferences(
            location="tokyo",
            budget="medium",
            cuisine="sushi",
            min_rating=4.0,
        )
        response = orchestrator.execute(preferences)

        assert response.meta["status"] == "empty"
        assert response.recommendations == []
        assert response.meta["candidates_sent_to_llm"] == 0
        engine = orchestrator.recommendation_engine
        assert isinstance(engine.llm_client, FakeLLMClient)
        assert engine.llm_client.calls == 0

    def test_store_not_loaded_raises(self, settings: Settings, tmp_path: Path) -> None:
        repo = RestaurantRepository(data_path=tmp_path / "missing.parquet", settings=settings)
        orchestrator = RecommendationOrchestrator(repository=repo, settings=settings)

        with pytest.raises(StoreNotLoadedError):
            orchestrator.execute(
                UserPreferences(
                    location="bangalore",
                    budget="medium",
                    cuisine="indian",
                    min_rating=4.0,
                )
            )
