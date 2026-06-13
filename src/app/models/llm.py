from pydantic import BaseModel, Field


class LLMRecommendationItem(BaseModel):
    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str = ""


class ParsedLLMResponse(BaseModel):
    summary: str | None = None
    recommendations: list[LLMRecommendationItem] = Field(default_factory=list)
