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

Rank and explain filtered candidates using **Groq**, with rating-based fallback when the provider or parser fails.

Configure `.env`:

```bash
LLM_PROVIDER=groq
LLM_API_KEY=gsk_...
LLM_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
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
- `GroqClient` — Groq chat completions with retry on timeout
- `ResponseParser` — JSON validation, markdown extraction, unknown ID filtering
- `RecommendationMerger` — joins LLM output to dataset rows, backfills to `top_k`
- `RecommendationEngine` — prompt → Groq → parse → merge with fallback

## Phase 4: Orchestrator & API

End-to-end pipeline behind a single entry point and FastAPI REST API.

```python
from app.models.preferences import UserPreferences
from app.services.orchestrator import RecommendationOrchestrator

preferences = UserPreferences(
    location="Bangalore",
    budget="medium",
    cuisine="North Indian",
    min_rating=4.0,
    top_k=5,
)

response = RecommendationOrchestrator().execute(preferences)
print(response.meta["status"], len(response.recommendations))
```

### Run API server

From the project root, use the project virtualenv (uvicorn is not on your global PATH):

```bash
# Recommended — uses .venv automatically
python scripts/run_backend.py

# Or activate the venv first, then run uvicorn
source .venv/bin/activate
uvicorn app.main:app --reload --app-dir src

# Or call uvicorn directly without activating
.venv/bin/uvicorn app.main:app --reload --app-dir src
```

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness + dataset status |
| `POST` | `/api/v1/recommendations` | Generate recommendations |
| `GET` | `/api/v1/metadata/locations` | Distinct cities |
| `GET` | `/api/v1/metadata/cuisines` | Distinct cuisines |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: demo-1" \
  -d '{"location":"Bangalore","budget":"medium","cuisine":"North Indian","min_rating":4.0,"top_k":5}'
```

## Phase 5: Frontend (DineAI — Stitch design)

React + Tailwind UI wired to the FastAPI backend. Start the API first, then the frontend.

```bash
# Terminal 1 — backend
python scripts/run_backend.py

# Terminal 2 — frontend (http://localhost:5173)
python scripts/run_frontend.py
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

### Legacy Streamlit UI

```bash
python scripts/run_ui.py
```

Deploy to [Streamlit Community Cloud](https://share.streamlit.io) using `src/app/ui/streamlit_app.py` as the main file. See [Deployment Plan](./docs/deployment-plan.md) for secrets, dataset packaging, and Docker.

## Run Tests

```bash
pytest
```

## Project Structure

```
src/app/
├── main.py                # FastAPI entry point
├── ui/
│   ├── streamlit_app.py   # Streamlit presentation layer (Phase 5)
│   └── components.py      # Formatting + form validation helpers
├── config.py              # Environment-driven settings
├── api/                   # REST routes, schemas, deps
├── models/                # Domain models (Restaurant, UserPreferences, …)
├── ingestion/             # HF load → normalize → preprocess → Parquet
├── services/
│   ├── filter_service.py
│   ├── orchestrator.py          # Full pipeline entry point
│   ├── prompt_builder.py
│   ├── llm_client.py            # GroqClient
│   ├── response_parser.py
│   ├── recommendation_merger.py
│   └── recommendation_engine.py
└── data/repository.py
```

## Configuration

See `.env.example` for:

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | Must be `groq` |
| `LLM_API_KEY` | Groq API key (`gsk_…`) |
| `LLM_MODEL` | Groq model (e.g. `llama-3.3-70b-versatile`) |
| `GROQ_BASE_URL` | Groq OpenAI-compatible API base |
| `DATA_PATH` | Processed Parquet file location |
| `HF_DATASET_ID` | Hugging Face dataset identifier |
| `BUDGET_LOW_MAX` | Cost ≤ this value → `low` band |
| `BUDGET_MEDIUM_MAX` | Cost ≤ this value → `medium` band; above → `high` |

## Docs

- [Context](./docs/context.md)
- [Architecture](./architecture.md)
- [Implementation Plan](./implementation-plan.md)
- [Deployment Plan](./docs/deployment-plan.md)
- [Edge Cases](./docs/edge-case.md)
