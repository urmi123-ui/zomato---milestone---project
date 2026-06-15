from __future__ import annotations

import logging
import time
import uuid

from app.config import Settings, get_settings
from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.models.recommendation import RecommendationResponse
from app.services.filter_service import FilterService
from app.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

EMPTY_FILTER_MESSAGE = (
    "No restaurants matched your filters. "
    "Try a different location, cuisine, or lower minimum rating."
)


class StoreNotLoadedError(Exception):
    """Raised when the restaurant dataset is unavailable."""


class RecommendationOrchestrator:
    """Single entry point: validate → filter → LLM → response."""

    def __init__(
        self,
        repository: RestaurantRepository | None = None,
        filter_service: FilterService | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.repository = repository or RestaurantRepository(settings=self.settings)
        self.filter_service = filter_service or FilterService(settings=self.settings)
        self.recommendation_engine = recommendation_engine or RecommendationEngine(settings=self.settings)

    def execute(
        self,
        preferences: UserPreferences,
        correlation_id: str | None = None,
    ) -> RecommendationResponse:
        correlation_id = correlation_id or uuid.uuid4().hex[:12]
        self._ensure_repository_loaded()

        logger.info(
            "Recommendation request started correlation_id=%s location=%s budget=%s cuisine=%s",
            correlation_id,
            preferences.location,
            preferences.budget,
            preferences.cuisine,
        )

        filter_start = time.perf_counter()
        filter_result = self.filter_service.filter(preferences, self.repository)
        filter_ms = (time.perf_counter() - filter_start) * 1000

        logger.info(
            "Filter complete correlation_id=%s matched=%d capped=%d filter_ms=%.1f",
            correlation_id,
            filter_result.total_before_cap,
            len(filter_result.candidates),
            filter_ms,
        )

        if filter_result.is_empty:
            return RecommendationResponse(
                summary=None,
                recommendations=[],
                meta={
                    "status": "empty",
                    "candidates_considered": 0,
                    "candidates_sent_to_llm": 0,
                    "filters_applied": filter_result.applied_filters,
                    "llm_fallback": False,
                    "correlation_id": correlation_id,
                    "filter_ms": round(filter_ms, 2),
                    "message": EMPTY_FILTER_MESSAGE,
                },
            )

        llm_start = time.perf_counter()
        response = self.recommendation_engine.generate(preferences, filter_result.candidates)
        llm_ms = (time.perf_counter() - llm_start) * 1000

        response.meta.update(
            {
                "candidates_considered": filter_result.total_before_cap,
                "candidates_sent_to_llm": len(filter_result.candidates),
                "filters_applied": filter_result.applied_filters,
                "correlation_id": correlation_id,
                "filter_ms": round(filter_ms, 2),
                "llm_latency_ms": round(llm_ms, 2),
                "llm_provider": self.settings.llm_provider,
                "llm_model": self.settings.llm_model,
                "was_capped": filter_result.was_capped,
            }
        )

        logger.info(
            "Recommendation complete correlation_id=%s status=%s llm_fallback=%s llm_ms=%.1f",
            correlation_id,
            response.meta.get("status"),
            response.meta.get("llm_fallback"),
            llm_ms,
        )
        return response

    def _ensure_repository_loaded(self) -> None:
        if self.repository.is_loaded:
            return
        try:
            self.repository.load()
        except Exception as exc:
            logger.error("Restaurant store failed to load: %s", exc)
            raise StoreNotLoadedError(str(exc)) from exc
