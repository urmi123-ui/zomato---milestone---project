import pytest

from app.services.response_parser import ResponseParser

VALID_JSON = """
{
  "summary": "Great North Indian picks in Bangalore.",
  "recommendations": [
    {
      "restaurant_id": "abc123",
      "rank": 1,
      "explanation": "Strong North Indian menu with family-friendly options."
    },
    {
      "restaurant_id": "def456",
      "rank": 2,
      "explanation": "Higher rating and quick service style dishes."
    }
  ]
}
"""

MARKDOWN_JSON = """
Here are my picks:
```json
{
  "summary": "Solid options.",
  "recommendations": [
    {"restaurant_id": "abc123", "rank": 1, "explanation": "Best fit."}
  ]
}
```
"""


@pytest.fixture
def parser() -> ResponseParser:
    return ResponseParser()


class TestResponseParser:
    def test_parses_valid_json(self, parser: ResponseParser) -> None:
        allowed = {"abc123", "def456"}
        parsed = parser.parse(VALID_JSON, allowed)

        assert parsed is not None
        assert parsed.summary == "Great North Indian picks in Bangalore."
        assert len(parsed.recommendations) == 2
        assert parsed.recommendations[0].restaurant_id == "abc123"
        assert parsed.recommendations[0].rank == 1

    def test_extracts_json_from_markdown_fence(self, parser: ResponseParser) -> None:
        parsed = parser.parse(MARKDOWN_JSON, {"abc123"})
        assert parsed is not None
        assert len(parsed.recommendations) == 1

    def test_drops_unknown_restaurant_ids(self, parser: ResponseParser) -> None:
        payload = """
        {
          "summary": "Test",
          "recommendations": [
            {"restaurant_id": "abc123", "rank": 1, "explanation": "Valid"},
            {"restaurant_id": "fake999", "rank": 2, "explanation": "Hallucinated"}
          ]
        }
        """
        parsed = parser.parse(payload, {"abc123"})
        assert parsed is not None
        assert len(parsed.recommendations) == 1
        assert parsed.recommendations[0].restaurant_id == "abc123"

    def test_deduplicates_restaurant_ids(self, parser: ResponseParser) -> None:
        payload = """
        {
          "recommendations": [
            {"restaurant_id": "abc123", "rank": 1, "explanation": "First"},
            {"restaurant_id": "abc123", "rank": 2, "explanation": "Duplicate"}
          ]
        }
        """
        parsed = parser.parse(payload, {"abc123"})
        assert parsed is not None
        assert len(parsed.recommendations) == 1

    def test_renumbers_ranks_sequentially(self, parser: ResponseParser) -> None:
        payload = """
        {
          "recommendations": [
            {"restaurant_id": "abc123", "rank": 5, "explanation": "A"},
            {"restaurant_id": "def456", "rank": 7, "explanation": "B"}
          ]
        }
        """
        parsed = parser.parse(payload, {"abc123", "def456"})
        assert parsed is not None
        assert [item.rank for item in parsed.recommendations] == [1, 2]

    def test_returns_none_for_invalid_json(self, parser: ResponseParser) -> None:
        assert parser.parse("not json at all", {"abc123"}) is None

    def test_returns_none_when_all_ids_invalid(self, parser: ResponseParser) -> None:
        payload = """
        {
          "recommendations": [
            {"restaurant_id": "fake1", "rank": 1, "explanation": "Bad"}
          ]
        }
        """
        assert parser.parse(payload, {"abc123"}) is None

    def test_uses_default_explanation_when_blank(self, parser: ResponseParser) -> None:
        payload = """
        {
          "recommendations": [
            {"restaurant_id": "abc123", "rank": 1, "explanation": "  "}
          ]
        }
        """
        parsed = parser.parse(payload, {"abc123"})
        assert parsed is not None
        assert parsed.recommendations[0].explanation
