# AI-Powered Restaurant Recommendation System

Zomato-inspired restaurant recommendations combining structured dataset filtering with LLM ranking and explanations.

## Prerequisites

- Python 3.11+
- Network access for first-time Hugging Face dataset download

## Setup

```bash
cd "zomato milestone"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

## Phase 1: Data Ingestion

Download and preprocess the [Zomato dataset from Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation):

```bash
# Option A: module entry point
python -m app.ingestion.pipeline

# Option B: script
python scripts/ingest.py
```

Output is written to `data/processed/restaurants.parquet` (configurable via `DATA_PATH` in `.env`).

### Verify ingestion

```python
from app.data.repository import RestaurantRepository

repo = RestaurantRepository()
repo.load()
print(repo.count(), "restaurants loaded")
print(repo.distinct_locations()[:5])
```

## Phase 2: Filter Layer

Deterministic candidate selection from user preferences (no LLM):

```python
from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.services.filter_service import FilterService

repo = RestaurantRepository()
repo.load()

preferences = UserPreferences(
    location="Bangalore",
    budget="medium",
    cuisine="North Indian",
    min_rating=4.0,
)

result = FilterService().filter(preferences, repo)
print(result.total_before_cap, "matched;", len(result.candidates), "candidates (capped)")
print(result.is_empty)  # False when matches exist
```

Hard filters: location (substring), budget band, cuisine (partial match), min rating. Results are sorted by rating → votes → name, capped at `MAX_CANDIDATES` (default 30).

## Phase 3: LLM Integration

Rank and explain filtered candidates using an LLM, with rating-based fallback when the provider or parser fails.

Configure `.env`:

```bash
LLM_PROVIDER=openai   # or ollama
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
```

```python
from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.services.filter_service import FilterService
from app.services.recommendation_engine import RecommendationEngine

repo = RestaurantRepository()
repo.load()

preferences = UserPreferences(
    location="Bangalore",
    budget="medium",
    cuisine="North Indian",
    min_rating=4.0,
    additional_preferences="family-friendly",
    top_k=5,
)

filter_result = FilterService().filter(preferences, repo)
response = RecommendationEngine().generate(preferences, filter_result.candidates)

for rec in response.recommendations:
    print(rec.rank, rec.restaurant.name, rec.explanation)
```

Components:
- `PromptBuilder` — grounded prompt with capped candidate JSON
- `LLMClient` — OpenAI and Ollama implementations with retry on timeout
- `ResponseParser` — JSON validation, markdown extraction, unknown ID filtering
- `RecommendationMerger` — joins LLM output to dataset rows, backfills to `top_k`
- `RecommendationEngine` — end-to-end generate with fallback

## Run Tests

```bash
pytest
```

## Project Structure

```
src/app/
├── config.py              # Environment-driven settings
├── models/                # Domain models (Restaurant, UserPreferences, …)
├── ingestion/             # HF load → normalize → preprocess → Parquet
├── services/
│   ├── filter_service.py        # Deterministic filter + sort + cap
│   ├── prompt_builder.py        # LLM prompt construction
│   ├── llm_client.py            # OpenAI / Ollama client
│   ├── response_parser.py       # Structured JSON parsing
│   ├── recommendation_merger.py # Join + fallback explanations
│   └── recommendation_engine.py # Prompt → LLM → parse → merge
└── data/repository.py     # Runtime read access to processed data
```

## Configuration

See `.env.example` for:

| Variable | Purpose |
|----------|---------|
| `DATA_PATH` | Processed Parquet file location |
| `HF_DATASET_ID` | Hugging Face dataset identifier |
| `BUDGET_LOW_MAX` | Cost ≤ this value → `low` band |
| `BUDGET_MEDIUM_MAX` | Cost ≤ this value → `medium` band; above → `high` |

## Docs

- [Context](./docs/context.md)
- [Architecture](./architecture.md)
- [Implementation Plan](./implementation-plan.md)
- [Edge Cases](./docs/edge-case.md)
