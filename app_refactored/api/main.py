"""FastAPI application entry point — Payment Orchestration Platform.

Refactored to follow digital-onboarding standards: LangGraph agents,
Redis session store, Phoenix observability integration, structured logging.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from shared.logger import setup_logging, get_logger
from observability.tracing import init_tracing
from api.routers import health, orchestrate

log = get_logger("api.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management: startup and shutdown."""
    setup_logging(level=settings.log_level)
    init_tracing()
    log.info("api.startup", env=settings.app_env, version="1.0.0")
    yield
    log.info("api.shutdown")


app = FastAPI(
    title="Payment Orchestration API",
    description=(
        "AI-powered payment rail orchestration — intelligent routing "
        "across SWIFT, ACH, and local payment networks using LangGraph agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration — environment-scoped
_cors_origins: list[str]
if settings.app_env == "development":
    _cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
else:
    # Production: explicitly configured
    _raw = settings.cors_allowed_origins
    _cors_origins = [o.strip() for o in _raw.split(",") if o.strip()]
    if not _cors_origins:
        raise RuntimeError(
            f"CORS_ALLOWED_ORIGINS must be set for app_env={settings.app_env!r}"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(orchestrate.router, prefix="/api/v1/payment", tags=["Payment Orchestration"])


@app.get("/")
async def root():
    """API root — returns info."""
    return {
        "service": "payment-orchestration",
        "version": "1.0.0",
        "docs": "/docs",
    }
