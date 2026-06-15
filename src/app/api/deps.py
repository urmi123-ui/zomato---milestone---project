"""FastAPI dependencies."""

from functools import lru_cache

from app.data.repository import RestaurantRepository
from app.services.orchestrator import RecommendationOrchestrator


@lru_cache
def get_repository() -> RestaurantRepository:
    return RestaurantRepository()


@lru_cache
def get_orchestrator() -> RecommendationOrchestrator:
    return RecommendationOrchestrator(repository=get_repository())
