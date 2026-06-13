from pydantic import BaseModel, Field

from app.models.restaurant import Restaurant


class Recommendation(BaseModel):
    restaurant: Restaurant
    rank: int = Field(ge=1)
    explanation: str


class RecommendationResponse(BaseModel):
    summary: str | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)
