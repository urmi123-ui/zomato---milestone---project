from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.ingestion.pipeline import run_ingestion


class DatasetBootstrapError(Exception):
    """Raised when the restaurant dataset cannot be prepared."""


def ensure_dataset(*, allow_ingest: bool = True) -> Path:
    """Return the dataset path, running ingestion on first boot when allowed."""
    settings = get_settings()
    path = settings.data_path

    if path.is_file():
        return path

    if not allow_ingest:
        raise DatasetBootstrapError(
            f"Restaurant dataset not found at {path}. "
            "Commit data/processed/restaurants.parquet or run ingestion locally."
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    count = run_ingestion(output_path=path)
    if count <= 0 or not path.is_file():
        raise DatasetBootstrapError("Ingestion completed but no restaurants were written.")

    return path
