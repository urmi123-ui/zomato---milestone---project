from typing import Literal

from pydantic import BaseModel, Field, field_validator


BudgetLevel = Literal["low", "medium", "high"]


class UserPreferences(BaseModel):
    location: str
    budget: BudgetLevel
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_preferences: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("location", "cuisine", mode="before")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("Expected string")
        stripped = value.strip()
        if not stripped:
            raise ValueError("Must not be empty")
        return stripped

    @field_validator("additional_preferences", mode="before")
    @classmethod
    def strip_optional_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped or None
