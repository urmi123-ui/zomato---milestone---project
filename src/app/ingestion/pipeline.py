from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from app.config import get_settings
from app.ingestion.loader import DatasetLoader
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.preprocessor import Preprocessor
from app.ingestion.writer import PersistenceWriter

logger = logging.getLogger(__name__)


def run_ingestion(dataset_id: str | None = None, output_path=None) -> int:
    settings = get_settings()
    dataset_id = dataset_id or settings.hf_dataset_id
    output_path = output_path or settings.data_path

    loader = DatasetLoader(dataset_id=dataset_id)
    rows = loader.load_as_records()

    normalizer = SchemaNormalizer(settings=settings)
    normalized = normalizer.normalize_batch(rows)
    logger.info("Normalized %d / %d rows", len(normalized), len(rows))

    preprocessor = Preprocessor()
    cleaned = preprocessor.process(normalized)

    writer = PersistenceWriter(output_path=output_path)
    writer.write(cleaned)
    return len(cleaned)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Ingest Zomato dataset from Hugging Face")
    parser.add_argument(
        "--dataset-id",
        default=None,
        help="Hugging Face dataset id (default: from settings)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output Parquet path (default: from settings)",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    if args.output is None:
        output_path = settings.data_path
    else:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = settings.data_path.parent / output_path

    try:
        count = run_ingestion(dataset_id=args.dataset_id, output_path=output_path)
        logger.info("Ingestion complete: %d restaurants written", count)
        return 0
    except Exception:
        logger.exception("Ingestion failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
