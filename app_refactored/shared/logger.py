"""Structured logging setup — compatible with Phoenix observability."""
from __future__ import annotations

import logging
import sys
from functools import lru_cache

from pythonjsonlogger import jsonlogger


def setup_logging(level: str = "INFO") -> None:
    """Configure JSON structured logging for all loggers."""
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # JSON handler to stdout
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(jsonlogger.JsonFormatter())
    root.addHandler(json_handler)

    # Suppress noisy libraries
    for name in ["urllib3", "botocore", "s3transfer", "sqlalchemy"]:
        logging.getLogger(name).setLevel(logging.WARNING)


@lru_cache(maxsize=1)
def get_logger(name: str) -> logging.LoggerAdapter:
    """Get a logger for a module — cached for performance."""
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, {})
