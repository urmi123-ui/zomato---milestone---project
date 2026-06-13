from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_max_retries: int = Field(default=1, ge=0, le=3)
    ollama_base_url: str = "http://localhost:11434"
    max_additional_preferences_length: int = Field(default=500, ge=50, le=2000)

    data_path: Path = Field(default=PROJECT_ROOT / "data/processed/restaurants.parquet")
    hf_dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"

    max_candidates: int = Field(default=30, ge=1, le=100)

    budget_low_max: float = Field(default=500.0, gt=0)
    budget_medium_max: float = Field(default=1500.0, gt=0)

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
