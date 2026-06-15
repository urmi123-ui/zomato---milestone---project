from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.exceptions import error_response
from app.api.routes import router
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="Zomato Restaurant Recommendations",
    description="AI-powered restaurant recommendations with Groq LLM ranking.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    message = exc.errors()[0]["msg"] if exc.errors() else "Invalid request"
    return JSONResponse(
        status_code=400,
        content=error_response("validation_error", message),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Zomato recommendation API", "docs": "/docs"}
