from __future__ import annotations

import logging
from typing import Any

from datasets import Dataset, load_dataset

logger = logging.getLogger(__name__)

DEFAULT_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


class DatasetLoader:
    """Fetch the Zomato dataset from Hugging Face."""

    def __init__(self, dataset_id: str = DEFAULT_DATASET_ID) -> None:
        self.dataset_id = dataset_id

    def load(self, split: str = "train") -> Dataset:
        logger.info("Loading dataset %s (split=%s)", self.dataset_id, split)
        dataset = load_dataset(self.dataset_id, split=split)
        logger.info("Loaded %d rows with columns: %s", len(dataset), dataset.column_names)
        return dataset

    def load_as_records(self, split: str = "train") -> list[dict[str, Any]]:
        dataset = self.load(split=split)
        return [dict(row) for row in dataset]
