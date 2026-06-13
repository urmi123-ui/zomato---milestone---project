from __future__ import annotations

import hashlib
import re
from typing import Any

from app.config import Settings
from app.models.restaurant import BudgetBand, Restaurant

# Hugging Face column → canonical field mapping (ManikaSaini/zomato-restaurant-recommendation)
HF_COLUMN_MAP = {
    "name": "name",
    "locality": "location",  # HF column `location` is locality (e.g. Banashankari)
    "address": "address",
    "cuisines": "cuisines",
    "cost": "approx_cost(for two people)",
    "rating": "rate",
    "votes": "votes",
    "rest_type": "rest_type",
    "online_order": "online_order",
    "book_table": "book_table",
    "url": "url",
}

REQUIRED_HF_COLUMNS = {"name", "address", "cuisines", "approx_cost(for two people)", "rate", "location"}


class SchemaNormalizer:
    """Map raw Hugging Face rows to canonical Restaurant models."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate_columns(self, row: dict[str, Any]) -> None:
        missing = REQUIRED_HF_COLUMNS - set(row.keys())
        if missing:
            raise ValueError(
                f"Dataset schema missing required columns: {sorted(missing)}. "
                f"Available: {sorted(row.keys())}. "
                f"Expected mapping: {HF_COLUMN_MAP}"
            )

    def normalize_row(self, row: dict[str, Any], row_index: int) -> Restaurant | None:
        name = _clean_string(row.get("name"))
        if not name:
            return None

        address = _clean_string(row.get("address")) or ""
        locality = _clean_string(row.get("location")) or ""
        city = _extract_city_from_address(address)
        location = _build_searchable_location(locality, city, address)

        cuisines = _parse_cuisines(row.get("cuisines"))
        rating = _parse_rating(row.get("rate"))
        estimated_cost = _parse_cost(row.get("approx_cost(for two people)"))
        budget_band = _cost_to_band(
            estimated_cost,
            self.settings.budget_low_max,
            self.settings.budget_medium_max,
        )

        restaurant_id = _generate_id(name, address, row_index)
        metadata = {
            "locality": locality,
            "city": city,
            "address": address,
            "votes": _parse_votes(row.get("votes")),
            "rest_type": _clean_string(row.get("rest_type")),
            "online_order": _clean_string(row.get("online_order")),
            "book_table": _clean_string(row.get("book_table")),
            "url": _clean_string(row.get("url")),
            "source_row_index": row_index,
        }

        return Restaurant(
            id=restaurant_id,
            name=name,
            location=location,
            cuisines=cuisines,
            rating=rating,
            estimated_cost=estimated_cost,
            budget_band=budget_band,
            metadata=metadata,
        )

    def normalize_batch(self, rows: list[dict[str, Any]]) -> list[Restaurant]:
        if not rows:
            return []
        self.validate_columns(rows[0])

        restaurants: list[Restaurant] = []
        for index, row in enumerate(rows):
            restaurant = self.normalize_row(row, index)
            if restaurant is not None:
                restaurants.append(restaurant)
        return restaurants


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_cuisines(value: Any) -> list[str]:
    text = _clean_string(value)
    if not text:
        return []
    return [part.strip().lower() for part in text.split(",") if part.strip()]


def _parse_rating(value: Any) -> float:
    text = _clean_string(value)
    if not text or text.upper() in {"NEW", "-", "NA", "N/A"}:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    rating = float(match.group(1))
    return max(0.0, min(5.0, rating))


def _parse_cost(value: Any) -> float | None:
    text = _clean_string(value)
    if not text or text in {"-", "NA", "N/A"}:
        return None
    numbers = re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    if not numbers:
        return None
    floats = [float(n) for n in numbers]
    if len(floats) >= 2 and ("-" in text or "to" in text.lower()):
        return max(floats)
    return floats[0]


def _parse_votes(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_city_from_address(address: str) -> str:
    if not address:
        return ""
    parts = [part.strip() for part in address.split(",") if part.strip()]
    if not parts:
        return ""
    city = parts[-1]
    return _normalize_city_name(city)


_CITY_ALIASES = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "banglore": "Bangalore",
    "bengalore": "Bangalore",
    "btm bangalore": "Bangalore",
    "new delhi": "New Delhi",
    "delhi": "Delhi",
}


def _normalize_city_name(city: str) -> str:
    key = city.strip().lower()
    return _CITY_ALIASES.get(key, city.strip())


def _build_searchable_location(locality: str, city: str, address: str) -> str:
    parts = [part for part in (locality, city) if part]
    if parts:
        return ", ".join(parts).lower()
    return address.lower()


def _cost_to_band(
    cost: float | None,
    low_max: float,
    medium_max: float,
) -> BudgetBand | None:
    if cost is None:
        return None
    if cost <= low_max:
        return "low"
    if cost <= medium_max:
        return "medium"
    return "high"


def _generate_id(name: str, address: str, row_index: int) -> str:
    payload = f"{name}|{address}|{row_index}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
