from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["groq"] = "groq"
    llm_api_key: str = ""
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_max_retries: int = Field(default=1, ge=0, le=3)
    groq_base_url: str = "https://api.groq.com/openai/v1"
    max_additional_preferences_length: int = Field(default=500, ge=50, le=2000)

    data_path: Path = Field(default=PROJECT_ROOT / "data/processed/restaurants.parquet")
    hf_dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"

    max_candidates: int = Field(default=30, ge=1, le=100)

    budget_low_max: float = Field(default=500.0, gt=0)
    budget_medium_max: float = Field(default=1500.0, gt=0)

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:8501,"
        "http://127.0.0.1:8501"
    )
    cors_origin_regex: str = ""

    @field_validator("data_path", mode="before")
    @classmethod
    def resolve_data_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @model_validator(mode="after")
    def validate_budget_thresholds(self) -> "Settings":
        if self.budget_low_max >= self.budget_medium_max:
            raise ValueError("budget_low_max must be less than budget_medium_max")
        return self

    @model_validator(mode="after")
    def resolve_groq_api_key(self) -> "Settings":
        if not self.llm_api_key and self.groq_api_key:
            self.llm_api_key = self.groq_api_key
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
