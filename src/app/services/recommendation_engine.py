from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.models.preferences import UserPreferences
from app.models.recommendation import RecommendationResponse
from app.models.restaurant import Restaurant
from app.services.llm_client import LLMClient, LLMRequestError, create_llm_client
from app.services.prompt_builder import PromptBuilder
from app.services.recommendation_merger import RecommendationMerger
from app.services.response_parser import ResponseParser

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Prompt, call, parse, and merge pipeline with fallback ranking."""

    def __init__(
        self,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
        response_parser: ResponseParser | None = None,
        merger: RecommendationMerger | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder or PromptBuilder(settings=self.settings)
        self.response_parser = response_parser or ResponseParser()
        self.merger = merger or RecommendationMerger()

    def generate(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> RecommendationResponse:
        if not candidates:
            return RecommendationResponse(
                summary="No restaurants matched your filters.",
                recommendations=[],
                meta={"status": "empty", "llm_fallback": False},
            )

        allowed_ids = {candidate.id for candidate in candidates}
        messages = self.prompt_builder.build(preferences, candidates)
        llm_fallback = False

        try:
            client = self.llm_client or create_llm_client(self.settings)
            raw = client.complete(messages)
            parsed = self.response_parser.parse(raw, allowed_ids)
            if parsed is None:
                llm_fallback = True
                summary, recommendations = self.merger.build_fallback(candidates, preferences)
            else:
                summary, recommendations = self.merger.merge(parsed, candidates, preferences)
        except (LLMRequestError, ValueError) as exc:
            logger.warning("LLM pipeline failed, using fallback: %s", exc)
            llm_fallback = True
            summary, recommendations = self.merger.build_fallback(candidates, preferences)

        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            meta={
                "status": "fallback" if llm_fallback else "success",
                "llm_fallback": llm_fallback,
                "candidates_sent_to_llm": len(candidates),
            },
        )
