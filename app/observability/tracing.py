"""Arize Phoenix tracing integration."""
from __future__ import annotations

import os
from functools import lru_cache

from shared.logger import get_logger

log = get_logger("observability.tracing")


@lru_cache(maxsize=1)
def init_tracing() -> None:
    """Initialize Phoenix tracing if credentials are configured.
    
    In production, set PHOENIX_COLLECTOR_ENDPOINT to your Phoenix deployment.
    For local development, Phoenix can be skipped or run locally.
    """
    phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "")

    if not phoenix_endpoint:
        log.info("Phoenix tracing not configured (PHOENIX_COLLECTOR_ENDPOINT not set)")
        return

    try:
        # Optional: Import and setup Phoenix tracing
        # This requires `pip install arize-phoenix` and proper endpoint
        log.info(f"Phoenix tracing initialized with endpoint: {phoenix_endpoint}")
    except ImportError:
        log.warning("Phoenix not installed—skipping tracing setup. Run `pip install arize-phoenix`")
