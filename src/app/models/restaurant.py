from typing import Any, Literal

from pydantic import BaseModel, Field


BudgetBand = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: list[str] = Field(default_factory=list)
    rating: float = 0.0
    estimated_cost: float | None = None
    budget_band: BudgetBand | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
