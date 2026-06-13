from __future__ import annotations

import json
import logging
import re

from pydantic import ValidationError

from app.models.llm import LLMRecommendationItem, ParsedLLMResponse

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parse and validate structured LLM JSON responses."""

    def parse(self, raw: str, allowed_ids: set[str]) -> ParsedLLMResponse | None:
        payload = self._load_json_payload(raw)
        if payload is None:
            return None

        try:
            parsed = ParsedLLMResponse.model_validate(payload)
        except ValidationError as exc:
            logger.warning("LLM JSON failed validation: %s", exc)
            return None

        sanitized = self._sanitize_recommendations(parsed.recommendations, allowed_ids)
        if not sanitized:
            logger.warning("No valid recommendations remained after sanitizing LLM output")
            return None

        return ParsedLLMResponse(summary=parsed.summary, recommendations=sanitized)

    def _load_json_payload(self, raw: str) -> dict | None:
        raw = raw.strip()
        if not raw:
            return None

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            extracted = _extract_json_block(raw)
            if extracted is None:
                logger.warning("Unable to parse LLM response as JSON")
                return None
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                logger.warning("Extracted JSON block is invalid")
                return None

    def _sanitize_recommendations(
        self,
        recommendations: list[LLMRecommendationItem],
        allowed_ids: set[str],
    ) -> list[LLMRecommendationItem]:
        seen_ids: set[str] = set()
        sanitized: list[LLMRecommendationItem] = []

        for index, item in enumerate(recommendations):
            if item.restaurant_id not in allowed_ids:
                logger.warning("Dropping unknown restaurant_id from LLM output: %s", item.restaurant_id)
                continue
            if item.restaurant_id in seen_ids:
                logger.warning("Dropping duplicate restaurant_id from LLM output: %s", item.restaurant_id)
                continue

            rank = item.rank if item.rank >= 1 else index + 1
            explanation = item.explanation.strip() or _default_explanation()
            sanitized.append(
                LLMRecommendationItem(
                    restaurant_id=item.restaurant_id,
                    rank=rank,
                    explanation=explanation,
                )
            )
            seen_ids.add(item.restaurant_id)

        sanitized.sort(key=lambda entry: entry.rank)
        for idx, item in enumerate(sanitized, start=1):
            if item.rank != idx:
                sanitized[idx - 1] = item.model_copy(update={"rank": idx})

        return sanitized


def _extract_json_block(text: str) -> str | None:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return None


def _default_explanation() -> str:
    return "Recommended based on your stated preferences."
