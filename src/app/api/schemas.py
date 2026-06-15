from typing import Literal

from pydantic import BaseModel, Field

from app.models.preferences import UserPreferences
from app.models.recommendation import Recommendation, RecommendationResponse


class RecommendationRequest(BaseModel):
    location: str = Field(min_length=1)
    budget: Literal["low", "medium", "high"]
    cuisine: str = Field(min_length=1)
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_preferences: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)

    def to_preferences(self) -> UserPreferences:
        return UserPreferences(
            location=self.location.strip(),
            budget=self.budget,
            cuisine=self.cuisine.strip(),
            min_rating=self.min_rating,
            additional_preferences=self.additional_preferences,
            top_k=self.top_k,
        )


class HealthResponse(BaseModel):
    status: str
    store_loaded: bool
    restaurant_count: int | None = None


class MetadataResponse(BaseModel):
    items: list[str]


RecommendationResponseSchema = RecommendationResponse

__all__ = [
    "HealthResponse",
    "MetadataResponse",
    "Recommendation",
    "RecommendationRequest",
    "RecommendationResponseSchema",
]
