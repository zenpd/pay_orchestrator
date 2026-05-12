from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import get_settings
from shared.logger import setup_logging, get_logger
from observability.tracing import init_tracing
from api.routers import health, payments, metrics, corridors, rails, logs

log = get_logger("api.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    init_tracing()
    log.info("api.startup", env=settings.app_env, version="1.0.0")
    yield
    log.info("api.shutdown")


app = FastAPI(
    title="Payment Orchestrator API",
    description="AI-powered cross-border payment orchestration platform with left-shifted compliance validation.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
if settings.app_env == "development":
    _cors_origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"]
else:
    _raw = settings.cors_allowed_origins
    _cors_origins = [o.strip() for o in _raw.split(",") if o.strip()]
    if not _cors_origins:
        raise RuntimeError(f"CORS_ALLOWED_ORIGINS must be set in app_env={settings.app_env!r}.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,      tags=["Health"])
app.include_router(payments.router,    prefix="/api/v1/payment",   tags=["Payments"])
app.include_router(metrics.router,     prefix="/api/v1/metrics",   tags=["Metrics"])
app.include_router(corridors.router,   prefix="/api/v1/corridors", tags=["Corridors"])
app.include_router(rails.router,       prefix="/api/v1/rails",     tags=["Rails"])
app.include_router(logs.router,        prefix="/api/v1/logs",      tags=["Logs"])
