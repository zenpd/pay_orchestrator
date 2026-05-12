from __future__ import annotations
from shared.config import get_settings
from shared.logger import get_logger

log = get_logger("observability.langsmith")


def init_langsmith() -> None:
    settings = get_settings()
    if settings.app_env == "development":
        import os
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_PROJECT", "pay-orchestrator")
        log.info("langsmith.enabled")
