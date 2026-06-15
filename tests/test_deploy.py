from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.config import clear_settings_cache, get_settings
from app.deploy.bootstrap import DatasetBootstrapError, ensure_dataset
from app.deploy.env import apply_streamlit_secrets


class TestApplyStreamlitSecrets:
    def setup_method(self) -> None:
        clear_settings_cache()
        for key in ("LLM_API_KEY", "DATA_PATH"):
            os.environ.pop(key, None)

    def teardown_method(self) -> None:
        clear_settings_cache()
        for key in ("LLM_API_KEY", "DATA_PATH"):
            os.environ.pop(key, None)

    def test_applies_root_level_secrets(self) -> None:
        mock_secrets = MagicMock()
        mock_secrets.items.return_value = [
            ("LLM_API_KEY", "gsk_test"),
            ("DATA_PATH", "data/processed/restaurants.parquet"),
            ("nested", {"ignored": True}),
        ]

        with patch("streamlit.secrets", mock_secrets):
            apply_streamlit_secrets()

        assert os.environ["LLM_API_KEY"] == "gsk_test"
        assert os.environ["DATA_PATH"] == "data/processed/restaurants.parquet"

    def test_does_not_override_existing_env(self) -> None:
        os.environ["LLM_API_KEY"] = "existing"

        mock_secrets = MagicMock()
        mock_secrets.items.return_value = [("LLM_API_KEY", "gsk_new")]

        with patch("streamlit.secrets", mock_secrets):
            apply_streamlit_secrets()

        assert os.environ["LLM_API_KEY"] == "existing"


class TestEnsureDataset:
    def test_returns_existing_path(self, tmp_path: Path) -> None:
        parquet = tmp_path / "restaurants.parquet"
        parquet.write_bytes(b"parquet")

        with patch("app.deploy.bootstrap.get_settings") as mock_settings:
            mock_settings.return_value.data_path = parquet
            result = ensure_dataset(allow_ingest=False)

        assert result == parquet

    def test_raises_when_missing_and_ingest_disabled(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.parquet"

        with patch("app.deploy.bootstrap.get_settings") as mock_settings:
            mock_settings.return_value.data_path = missing
            with pytest.raises(DatasetBootstrapError, match="not found"):
                ensure_dataset(allow_ingest=False)

    def test_runs_ingestion_when_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "restaurants.parquet"

        with (
            patch("app.deploy.bootstrap.get_settings") as mock_settings,
            patch("app.deploy.bootstrap.run_ingestion", return_value=10) as mock_ingest,
        ):
            mock_settings.return_value.data_path = missing

            def write_file(**kwargs: object) -> int:
                missing.parent.mkdir(parents=True, exist_ok=True)
                missing.write_bytes(b"parquet")
                return 10

            mock_ingest.side_effect = write_file
            result = ensure_dataset(allow_ingest=True)

        assert result == missing
        mock_ingest.assert_called_once_with(output_path=missing)

    def test_settings_reads_env_after_secrets_applied(self, tmp_path: Path) -> None:
        clear_settings_cache()
        os.environ["DATA_PATH"] = str(tmp_path / "custom.parquet")

        settings = get_settings()
        assert settings.data_path == tmp_path / "custom.parquet"

        clear_settings_cache()
        os.environ.pop("DATA_PATH", None)


class TestCorsSettings:
    def test_default_cors_origins_include_local_dev(self) -> None:
        clear_settings_cache()
        settings = get_settings()
        origins = settings.cors_origin_list
        assert "http://localhost:5173" in origins
        assert "http://127.0.0.1:8501" in origins

    def test_cors_origins_parsed_from_env(self) -> None:
        clear_settings_cache()
        os.environ["CORS_ORIGINS"] = "https://app.vercel.app, http://localhost:3000"
        try:
            settings = get_settings()
            assert settings.cors_origin_list == [
                "https://app.vercel.app",
                "http://localhost:3000",
            ]
        finally:
            clear_settings_cache()
            os.environ.pop("CORS_ORIGINS", None)
