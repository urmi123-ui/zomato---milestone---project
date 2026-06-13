from pathlib import Path

import pytest

from app.config import Settings
from app.data.repository import RestaurantRepository
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.preprocessor import Preprocessor
from app.ingestion.writer import PersistenceWriter
from app.models.preferences import UserPreferences
from app.services.filter_service import FilterService
from tests.test_schema_normalizer import SAMPLE_HF_ROW


def _row(**overrides: object) -> dict:
    return {**SAMPLE_HF_ROW, **overrides}


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_path=tmp_path / "restaurants.parquet",
        budget_low_max=500,
        budget_medium_max=1500,
        max_candidates=3,
    )


@pytest.fixture
def repository(settings: Settings) -> RestaurantRepository:
    normalizer = SchemaNormalizer(settings=settings)
    rows = [
        _row(name="Jalsa", rate="4.1/5", votes=775, cuisines="North Indian, Mughlai, Chinese", **{"approx_cost(for two people)": "800"}),
        _row(name="Spice Elephant", rate="4.5/5", votes=900, cuisines="Chinese, North Indian, Thai", **{"approx_cost(for two people)": "800"}),
        _row(name="Mughlai Magic", rate="4.3/5", votes=500, cuisines="North Indian, Mughlai", **{"approx_cost(for two people)": "900"}),
        _row(name="Indian Spice Hub", rate="4.2/5", votes=650, cuisines="North Indian", **{"approx_cost(for two people)": "700"}),
        _row(name="Curry Corner", rate="4.0/5", votes=400, cuisines="North Indian, Chinese", **{"approx_cost(for two people)": "600"}),
        _row(name="Budget Bites", rate="4.8/5", votes=50, cuisines="North Indian", **{"approx_cost(for two people)": "300"}),
        _row(name="Premium Palace", rate="4.9/5", votes=1200, cuisines="Italian, Continental", **{"approx_cost(for two people)": "2000"}),
        _row(name="Low Rated Spot", rate="3.2/5", votes=200, cuisines="North Indian", **{"approx_cost(for two people)": "400"}),
        _row(
            name="Delhi Darbar",
            address="123, Connaught Place, New Delhi",
            location="Connaught Place",
            cuisines="North Indian, Mughlai",
            rate="4.5/5",
            votes=600,
            **{"approx_cost(for two people)": "400"},
        ),
        _row(name="Unknown Cost Cafe", rate="4.0/5", votes=100, cuisines="Cafe", **{"approx_cost(for two people)": "-"}),
    ]
    restaurants = Preprocessor().process(normalizer.normalize_batch(rows))
    PersistenceWriter(settings.data_path).write(restaurants)
    repo = RestaurantRepository(data_path=settings.data_path, settings=settings)
    repo.load()
    return repo


@pytest.fixture
def filter_service(settings: Settings) -> FilterService:
    return FilterService(settings=settings)


class TestFilterServiceLocation:
    def test_matches_city_substring(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert not result.is_empty
        assert all("bangalore" in candidate.location for candidate in result.candidates)

    def test_unknown_location_returns_empty(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="tokyo",
            budget="medium",
            cuisine="indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert result.is_empty
        assert result.candidates == []
        assert result.total_before_cap == 0


class TestFilterServiceBudget:
    def test_matches_budget_band(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="low",
            cuisine="indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert not result.is_empty
        assert all(candidate.budget_band == "low" for candidate in result.candidates)
        assert any(candidate.name == "Budget Bites" for candidate in result.candidates)

    def test_excludes_unknown_budget_band(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="cafe",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert result.is_empty


class TestFilterServiceCuisine:
    def test_partial_cuisine_match(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="Indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert not result.is_empty
        assert all(
            any("indian" in cuisine for cuisine in candidate.cuisines)
            for candidate in result.candidates
        )

    def test_italian_filter(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="high",
            cuisine="italian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert len(result.candidates) == 1
        assert result.candidates[0].name == "Premium Palace"


class TestFilterServiceRating:
    def test_min_rating_excludes_lower_rated(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="low",
            cuisine="indian",
            min_rating=4.0,
        )
        result = filter_service.filter(preferences, repository)
        assert all(candidate.rating >= 4.0 for candidate in result.candidates)
        assert not any(candidate.name == "Low Rated Spot" for candidate in result.candidates)


class TestFilterServiceCapAndSort:
    def test_caps_candidates_at_max(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        assert len(result.candidates) == 3
        assert result.total_before_cap > len(result.candidates)
        assert result.was_capped

    def test_sorts_by_rating_then_votes(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=0.0,
        )
        result = filter_service.filter(preferences, repository)
        ratings = [candidate.rating for candidate in result.candidates]
        assert ratings == sorted(ratings, reverse=True)
        assert result.candidates[0].name == "Spice Elephant"

    def test_single_candidate_not_capped(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        preferences = UserPreferences(
            location="bangalore",
            budget="high",
            cuisine="italian",
            min_rating=4.0,
        )
        result = filter_service.filter(preferences, repository)
        assert len(result.candidates) == 1
        assert result.total_before_cap == 1
        assert not result.was_capped


class TestFilterServiceMetadata:
    def test_applied_filters_excludes_additional_preferences(
        self,
        filter_service: FilterService,
        repository: RestaurantRepository,
    ) -> None:
        base = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=4.0,
        )
        with_extra = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=4.0,
            additional_preferences="family-friendly, quick service",
        )
        base_result = filter_service.filter(base, repository)
        extra_result = filter_service.filter(with_extra, repository)

        assert base_result.total_before_cap == extra_result.total_before_cap
        assert [candidate.id for candidate in base_result.candidates] == [
            candidate.id for candidate in extra_result.candidates
        ]
        assert "additional_preferences" not in base_result.applied_filters
        assert base_result.applied_filters == {
            "location": "bangalore",
            "budget": "medium",
            "cuisine": "indian",
            "min_rating": 4.0,
        }

    def test_empty_result_is_distinguishable(self, filter_service: FilterService, repository: RestaurantRepository) -> None:
        empty = filter_service.filter(
            UserPreferences(location="tokyo", budget="low", cuisine="sushi", min_rating=4.0),
            repository,
        )
        success = filter_service.filter(
            UserPreferences(location="bangalore", budget="high", cuisine="italian", min_rating=4.0),
            repository,
        )
        assert empty.is_empty
        assert not success.is_empty


class TestFilterServicePerformance:
    @pytest.mark.skipif(
        not Path("data/processed/restaurants.parquet").exists(),
        reason="Processed dataset not available",
    )
    def test_filter_completes_within_budget(self) -> None:
        import time

        settings = Settings(max_candidates=30)
        repository = RestaurantRepository(settings=settings)
        repository.load()
        filter_service = FilterService(settings=settings)
        preferences = UserPreferences(
            location="bangalore",
            budget="medium",
            cuisine="indian",
            min_rating=3.5,
        )

        start = time.perf_counter()
        result = filter_service.filter(preferences, repository)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(result.candidates) <= 30
        assert elapsed_ms < 100, f"Filter took {elapsed_ms:.1f} ms"
