from __future__ import annotations

import logging

from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class Preprocessor:
    """Clean and validate normalized restaurants before persistence."""

    def process(self, restaurants: list[Restaurant]) -> list[Restaurant]:
        cleaned: list[Restaurant] = []
        dropped = 0

        for restaurant in restaurants:
            if not restaurant.name.strip():
                dropped += 1
                continue

            cleaned.append(
                restaurant.model_copy(
                    update={
                        "name": restaurant.name.strip(),
                        "location": restaurant.location.strip().lower(),
                        "cuisines": [c.strip().lower() for c in restaurant.cuisines if c.strip()],
                    }
                )
            )

        if dropped:
            logger.info("Preprocessor dropped %d rows with empty names", dropped)

        if not cleaned:
            raise ValueError("All rows were dropped during preprocessing; no valid restaurants remain.")

        return cleaned
