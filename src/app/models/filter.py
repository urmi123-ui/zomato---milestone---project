from pydantic import BaseModel, Field

from app.models.preferences import BudgetLevel
from app.models.restaurant import Restaurant


class FilterCriteria(BaseModel):
    location: str
    budget: BudgetLevel
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_preferences: str | None = None


class FilterResult(BaseModel):
    candidates: list[Restaurant] = Field(default_factory=list)
    total_before_cap: int = 0
    applied_filters: dict[str, str | float] = Field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """True when no restaurants matched hard filters (orchestrator should skip LLM)."""
        return self.total_before_cap == 0

    @property
    def was_capped(self) -> bool:
        return self.total_before_cap > len(self.candidates)
