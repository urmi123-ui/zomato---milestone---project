import pytest

from app.config import Settings
from app.ingestion.normalizer import SchemaNormalizer

SAMPLE_HF_ROW = {
    "url": "https://www.zomato.com/bangalore/jalsa-banashankari",
    "address": "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore",
    "name": "Jalsa",
    "online_order": "Yes",
    "book_table": "Yes",
    "rate": "4.1/5",
    "votes": 775,
    "phone": "080 42297555",
    "location": "Banashankari",
    "rest_type": "Casual Dining",
    "dish_liked": "Pasta, Lunch Buffet",
    "cuisines": "North Indian, Mughlai, Chinese",
    "approx_cost(for two people)": "800",
    "reviews_list": "[]",
    "menu_item": "[]",
    "listed_in(type)": "Buffet",
    "listed_in(city)": "Banashankari",
}


@pytest.fixture
def settings() -> Settings:
    return Settings(
        budget_low_max=500,
        budget_medium_max=1500,
    )


@pytest.fixture
def normalizer(settings: Settings) -> SchemaNormalizer:
    return SchemaNormalizer(settings=settings)


class TestSchemaNormalizer:
    def test_maps_hf_row_to_restaurant(self, normalizer: SchemaNormalizer) -> None:
        restaurant = normalizer.normalize_row(SAMPLE_HF_ROW, row_index=0)

        assert restaurant is not None
        assert restaurant.name == "Jalsa"
        assert restaurant.rating == pytest.approx(4.1)
        assert restaurant.estimated_cost == pytest.approx(800.0)
        assert restaurant.budget_band == "medium"
        assert restaurant.cuisines == ["north indian", "mughlai", "chinese"]
        assert "bangalore" in restaurant.location
        assert restaurant.metadata["city"] == "Bangalore"
        assert restaurant.metadata["votes"] == 775

    def test_skips_empty_name(self, normalizer: SchemaNormalizer) -> None:
        row = {**SAMPLE_HF_ROW, "name": "   "}
        assert normalizer.normalize_row(row, row_index=1) is None

    def test_parse_rating_new(self, normalizer: SchemaNormalizer) -> None:
        row = {**SAMPLE_HF_ROW, "rate": "NEW"}
        restaurant = normalizer.normalize_row(row, row_index=2)
        assert restaurant is not None
        assert restaurant.rating == 0.0

    def test_parse_cost_range(self, normalizer: SchemaNormalizer) -> None:
        row = {**SAMPLE_HF_ROW, "approx_cost(for two people)": "300-500"}
        restaurant = normalizer.normalize_row(row, row_index=3)
        assert restaurant is not None
        assert restaurant.estimated_cost == pytest.approx(500.0)
        assert restaurant.budget_band == "low"

    def test_budget_band_boundaries(self, normalizer: SchemaNormalizer) -> None:
        for cost, expected in [(500, "low"), (501, "medium"), (1500, "medium"), (1501, "high")]:
            row = {**SAMPLE_HF_ROW, "approx_cost(for two people)": str(cost)}
            restaurant = normalizer.normalize_row(row, row_index=cost)
            assert restaurant is not None
            assert restaurant.budget_band == expected

    def test_cuisine_normalization(self, normalizer: SchemaNormalizer) -> None:
        row = {**SAMPLE_HF_ROW, "cuisines": " Italian, chinese , "}
        restaurant = normalizer.normalize_row(row, row_index=4)
        assert restaurant is not None
        assert restaurant.cuisines == ["italian", "chinese"]

    def test_missing_required_columns_raises(self, normalizer: SchemaNormalizer) -> None:
        with pytest.raises(ValueError, match="missing required columns"):
            normalizer.normalize_batch([{"name": "Only Name"}])

    def test_stable_id_generation(self, normalizer: SchemaNormalizer) -> None:
        first = normalizer.normalize_row(SAMPLE_HF_ROW, row_index=0)
        second = normalizer.normalize_row(SAMPLE_HF_ROW, row_index=0)
        assert first is not None and second is not None
        assert first.id == second.id

    def test_batch_normalization(self, normalizer: SchemaNormalizer) -> None:
        rows = [SAMPLE_HF_ROW, {**SAMPLE_HF_ROW, "name": ""}, {**SAMPLE_HF_ROW, "name": "Spice Elephant"}]
        restaurants = normalizer.normalize_batch(rows)
        assert len(restaurants) == 2
