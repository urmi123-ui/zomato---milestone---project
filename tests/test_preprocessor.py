import pytest

from app.ingestion.preprocessor import Preprocessor
from app.ingestion.normalizer import SchemaNormalizer
from app.config import Settings
from app.models.restaurant import Restaurant
from tests.test_schema_normalizer import SAMPLE_HF_ROW


@pytest.fixture
def settings() -> Settings:
    return Settings(budget_low_max=500, budget_medium_max=1500)


def test_preprocessor_drops_empty_names(settings: Settings) -> None:
    normalizer = SchemaNormalizer(settings=settings)
    restaurants = normalizer.normalize_batch([SAMPLE_HF_ROW, {**SAMPLE_HF_ROW, "name": "  "}])

    cleaned = Preprocessor().process(restaurants)
    assert len(cleaned) == 1


def test_preprocessor_raises_when_all_dropped() -> None:
    restaurants = [
        Restaurant(
            id="x",
            name=" ",
            location="test",
            cuisines=[],
            rating=0.0,
        )
    ]
    with pytest.raises(ValueError, match="All rows were dropped"):
        Preprocessor().process(restaurants)
