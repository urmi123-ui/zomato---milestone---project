from __future__ import annotations

import logging
from pathlib import Path

from app.config import Settings, get_settings
from app.ingestion.writer import PersistenceWriter
from app.models.filter import FilterCriteria
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """Read-only access to preprocessed restaurant data."""

    def __init__(self, data_path: Path | None = None, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._data_path = data_path or self._settings.data_path
        self._restaurants: list[Restaurant] | None = None
        self._by_id: dict[str, Restaurant] | None = None
        self._load_error: str | None = None

    @property
    def data_path(self) -> Path:
        return self._data_path

    @property
    def is_loaded(self) -> bool:
        return self._restaurants is not None

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def load(self, force: bool = False) -> None:
        if self.is_loaded and not force:
            return

        try:
            restaurants = PersistenceWriter.read_parquet(self._data_path)
            self._restaurants = restaurants
            self._by_id = {restaurant.id: restaurant for restaurant in restaurants}
            self._load_error = None
            logger.info("Loaded %d restaurants from %s", len(restaurants), self._data_path)
        except Exception as exc:
            self._restaurants = None
            self._by_id = None
            self._load_error = str(exc)
            logger.error("Failed to load restaurant data: %s", exc)
            raise

    def ensure_loaded(self) -> None:
        if not self.is_loaded:
            self.load()

    def get_all(self) -> list[Restaurant]:
        self.ensure_loaded()
        assert self._restaurants is not None
        return list(self._restaurants)

    def get_by_ids(self, ids: list[str]) -> list[Restaurant]:
        self.ensure_loaded()
        assert self._by_id is not None
        results: list[Restaurant] = []
        for restaurant_id in ids:
            restaurant = self._by_id.get(restaurant_id)
            if restaurant is not None:
                results.append(restaurant)
        return results

    def filter(self, criteria: FilterCriteria) -> list[Restaurant]:
        self.ensure_loaded()
        assert self._restaurants is not None

        location_query = criteria.location.strip().lower()
        cuisine_query = criteria.cuisine.strip().lower()

        matched: list[Restaurant] = []
        for restaurant in self._restaurants:
            if location_query and location_query not in restaurant.location:
                continue
            if restaurant.budget_band != criteria.budget:
                continue
            if cuisine_query and not any(cuisine_query in cuisine for cuisine in restaurant.cuisines):
                continue
            if restaurant.rating < criteria.min_rating:
                continue
            matched.append(restaurant)

        return matched

    def count(self) -> int:
        self.ensure_loaded()
        assert self._restaurants is not None
        return len(self._restaurants)

    def distinct_locations(self) -> list[str]:
        self.ensure_loaded()
        assert self._restaurants is not None
        cities = sorted(
            {
                restaurant.metadata.get("city", "").strip()
                for restaurant in self._restaurants
                if restaurant.metadata.get("city")
            }
        )
        return cities

    def distinct_areas(self) -> list[str]:
        self.ensure_loaded()
        assert self._restaurants is not None
        areas = sorted(
            {
                restaurant.metadata.get("locality", "").strip()
                for restaurant in self._restaurants
                if restaurant.metadata.get("locality")
            }
        )
        return areas

    def distinct_cuisines(self) -> list[str]:
        self.ensure_loaded()
        assert self._restaurants is not None
        cuisines = sorted({cuisine for restaurant in self._restaurants for cuisine in restaurant.cuisines})
        return cuisines
