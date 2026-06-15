from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_orchestrator, get_repository
from app.config import Settings
from app.data.repository import RestaurantRepository
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.preprocessor import Preprocessor
from app.ingestion.writer import PersistenceWriter
from app.main import app
from app.services.filter_service import FilterService
from app.services.orchestrator import RecommendationOrchestrator
from app.services.recommendation_engine import RecommendationEngine
from tests.test_orchestrator import FakeLLMClient
from tests.test_schema_normalizer import SAMPLE_HF_ROW


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_path=tmp_path / "restaurants.parquet",
        budget_low_max=500,
        budget_medium_max=1500,
        llm_provider="groq",
        llm_api_key="gsk_test",
    )


@pytest.fixture
def repository(settings: Settings) -> RestaurantRepository:
    normalizer = SchemaNormalizer(settings=settings)
    restaurants = Preprocessor().process(normalizer.normalize_batch([SAMPLE_HF_ROW]))
    PersistenceWriter(settings.data_path).write(restaurants)
    repo = RestaurantRepository(data_path=settings.data_path, settings=settings)
    repo.load()
    return repo


@pytest.fixture
def orchestrator(settings: Settings, repository: RestaurantRepository) -> RecommendationOrchestrator:
    restaurant_id = repository.get_all()[0].id
    llm = FakeLLMClient(
        response=f"""
        {{
          "summary": "Great option.",
          "recommendations": [
            {{"restaurant_id": "{restaurant_id}", "rank": 1, "explanation": "Perfect fit."}}
          ]
        }}
        """
    )
    engine = RecommendationEngine(settings=settings, llm_client=llm)
    return RecommendationOrchestrator(
        repository=repository,
        filter_service=FilterService(settings=settings),
        recommendation_engine=engine,
        settings=settings,
    )


@pytest.fixture
def client(repository: RestaurantRepository, orchestrator: RecommendationOrchestrator) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRecommendationAPI:
    def test_health_ok(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["store_loaded"] is True

    def test_metadata_locations(self, client: TestClient) -> None:
        response = client.get("/api/v1/metadata/locations")
        assert response.status_code == 200
        assert "items" in response.json()

    def test_metadata_cuisines(self, client: TestClient) -> None:
        response = client.get("/api/v1/metadata/cuisines")
        assert response.status_code == 200
        assert isinstance(response.json()["items"], list)

    def test_create_recommendations(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "location": "bangalore",
                "budget": "medium",
                "cuisine": "north indian",
                "min_rating": 4.0,
                "top_k": 1,
            },
            headers={"X-Correlation-ID": "api-test-1"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["meta"]["correlation_id"] == "api-test-1"
        assert len(payload["recommendations"]) >= 1

    def test_validation_error_on_empty_location(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "location": "   ",
                "budget": "medium",
                "cuisine": "indian",
                "min_rating": 4.0,
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "validation_error"

    def test_health_503_when_store_missing(self, settings: Settings, tmp_path: Path) -> None:
        missing_repo = RestaurantRepository(data_path=tmp_path / "missing.parquet", settings=settings)
        app.dependency_overrides[get_repository] = lambda: missing_repo
        app.dependency_overrides[get_orchestrator] = lambda: RecommendationOrchestrator(
            repository=missing_repo,
            settings=settings,
        )
        try:
            response = TestClient(app).get("/api/v1/health")
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "store_not_loaded"
        finally:
            app.dependency_overrides.clear()
