from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class PersistenceWriter:
    """Write processed restaurants to Parquet with atomic replace."""

    MANIFEST_SUFFIX = ".manifest.json"

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def write(self, restaurants: list[Restaurant]) -> Path:
        if not restaurants:
            raise ValueError("Refusing to write empty restaurant dataset.")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        records = [restaurant.model_dump() for restaurant in restaurants]
        frame = pd.DataFrame(records)

        temp_path = self.output_path.with_suffix(".parquet.tmp")
        frame.to_parquet(temp_path, index=False)
        temp_path.replace(self.output_path)

        manifest_path = self.output_path.with_suffix(self.MANIFEST_SUFFIX)
        manifest = {
            "row_count": len(restaurants),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "output_path": str(self.output_path),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        logger.info("Wrote %d restaurants to %s", len(restaurants), self.output_path)
        return self.output_path

    @staticmethod
    def read_parquet(path: Path) -> list[Restaurant]:
        if not path.exists():
            raise FileNotFoundError(f"Processed dataset not found at {path}")

        frame = pd.read_parquet(path)
        if frame.empty:
            raise ValueError(f"Processed dataset at {path} is empty.")

        restaurants: list[Restaurant] = []
        for record in frame.to_dict(orient="records"):
            restaurants.append(Restaurant.model_validate(_sanitize_record(record)))
        return restaurants


def _sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, float) and math.isnan(value):
            cleaned[key] = None
        elif key == "metadata" and isinstance(value, dict):
            cleaned[key] = {
                meta_key: None if isinstance(meta_value, float) and math.isnan(meta_value) else meta_value
                for meta_key, meta_value in value.items()
            }
        else:
            cleaned[key] = value
    return cleaned
