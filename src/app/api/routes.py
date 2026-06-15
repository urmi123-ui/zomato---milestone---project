from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import get_orchestrator, get_repository
from app.api.exceptions import error_response
from app.api.schemas import HealthResponse, MetadataResponse, RecommendationRequest
from app.data.repository import RestaurantRepository
from app.models.recommendation import RecommendationResponse
from app.services.orchestrator import RecommendationOrchestrator, StoreNotLoadedError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(repository: RestaurantRepository = Depends(get_repository)) -> HealthResponse | JSONResponse:
    if not repository.is_loaded:
        try:
            repository.load()
        except Exception:
            return JSONResponse(
                status_code=503,
                content=error_response("store_not_loaded", "Restaurant dataset is not loaded."),
            )

    return HealthResponse(
        status="ok",
        store_loaded=True,
        restaurant_count=repository.count(),
    )


@router.get("/metadata/locations", response_model=MetadataResponse)
def list_locations(repository: RestaurantRepository = Depends(get_repository)) -> MetadataResponse | JSONResponse:
    try:
        _ensure_loaded(repository)
    except StoreNotLoadedError:
        return JSONResponse(
            status_code=503,
            content=error_response("store_not_loaded", "Restaurant dataset is not loaded."),
        )
    return MetadataResponse(items=repository.distinct_locations())


@router.get("/metadata/cuisines", response_model=MetadataResponse)
def list_cuisines(repository: RestaurantRepository = Depends(get_repository)) -> MetadataResponse | JSONResponse:
    try:
        _ensure_loaded(repository)
    except StoreNotLoadedError:
        return JSONResponse(
            status_code=503,
            content=error_response("store_not_loaded", "Restaurant dataset is not loaded."),
        )
    return MetadataResponse(items=repository.distinct_cuisines())


@router.get("/metadata/areas", response_model=MetadataResponse)
def list_areas(repository: RestaurantRepository = Depends(get_repository)) -> MetadataResponse | JSONResponse:
    try:
        _ensure_loaded(repository)
    except StoreNotLoadedError:
        return JSONResponse(
            status_code=503,
            content=error_response("store_not_loaded", "Restaurant dataset is not loaded."),
        )
    return MetadataResponse(items=repository.distinct_areas())


@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendations(
    request: Request,
    body: RecommendationRequest,
    orchestrator: RecommendationOrchestrator = Depends(get_orchestrator),
) -> RecommendationResponse | JSONResponse:
    correlation_id = request.headers.get("X-Correlation-ID")

    try:
        preferences = body.to_preferences()
    except PydanticValidationError as exc:
        return JSONResponse(
            status_code=400,
            content=error_response("validation_error", str(exc.errors()[0]["msg"])),
        )

    try:
        return orchestrator.execute(preferences, correlation_id=correlation_id)
    except StoreNotLoadedError as exc:
        return JSONResponse(
            status_code=503,
            content=error_response("store_not_loaded", str(exc)),
        )
    except Exception as exc:
        logger.exception("Unexpected recommendation failure correlation_id=%s", correlation_id)
        return JSONResponse(
            status_code=502,
            content=error_response("recommendation_failed", str(exc)),
        )


def _ensure_loaded(repository: RestaurantRepository) -> None:
    if repository.is_loaded:
        return
    try:
        repository.load()
    except Exception as exc:
        raise StoreNotLoadedError(str(exc)) from exc
