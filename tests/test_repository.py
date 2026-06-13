from pathlib import Path

import pytest

from app.config import Settings
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.preprocessor import Preprocessor
from app.ingestion.writer import PersistenceWriter
from app.models.filter import FilterCriteria
from app.data.repository import RestaurantRepository
from tests.test_schema_normalizer import SAMPLE_HF_ROW


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_path=tmp_path / "restaurants.parquet",
        budget_low_max=500,
        budget_medium_max=1500,
    )


@pytest.fixture
def parquet_path(settings: Settings, tmp_path: Path) -> Path:
    normalizer = SchemaNormalizer(settings=settings)
    rows = [
        SAMPLE_HF_ROW,
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
    return PersistenceWriter(settings.data_path).write(restaurants)


class TestRestaurantRepository:
    def test_load_and_get_all(self, settings: Settings, parquet_path: Path) -> None:
        repo = RestaurantRepository(data_path=parquet_path, settings=settings)
        repo.load()

        assert repo.is_loaded
        assert repo.count() == 2
        assert len(repo.get_all()) == 2

    def test_get_by_ids(self, settings: Settings, parquet_path: Path) -> None:
        repo = RestaurantRepository(data_path=parquet_path, settings=settings)
        repo.load()
        all_ids = [restaurant.id for restaurant in repo.get_all()]

        found = repo.get_by_ids([all_ids[0], "missing-id"])
        assert len(found) == 1
        assert found[0].id == all_ids[0]

    def test_filter_by_location_and_cuisine(self, settings: Settings, parquet_path: Path) -> None:
        repo = RestaurantRepository(data_path=parquet_path, settings=settings)
        repo.load()

        criteria = FilterCriteria(
            location="bangalore",
            budget="medium",
            cuisine="north indian",
            min_rating=4.0,
        )
        results = repo.filter(criteria)
        assert len(results) == 1
        assert results[0].name == "Jalsa"

    def test_filter_empty_when_no_match(self, settings: Settings, parquet_path: Path) -> None:
        repo = RestaurantRepository(data_path=parquet_path, settings=settings)
        repo.load()

        criteria = FilterCriteria(
            location="tokyo",
            budget="low",
            cuisine="sushi",
            min_rating=4.0,
        )
        assert repo.filter(criteria) == []

    def test_load_missing_file_raises(self, settings: Settings, tmp_path: Path) -> None:
        repo = RestaurantRepository(data_path=tmp_path / "missing.parquet", settings=settings)
        with pytest.raises(FileNotFoundError):
            repo.load()
