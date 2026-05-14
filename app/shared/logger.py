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


class StructlogAdapter(logging.LoggerAdapter):
    """Logger adapter that accepts structlog-style keyword arguments."""

    def process(self, msg, kwargs):
        extra_kwargs = {k: v for k, v in kwargs.items() if k not in (
            'exc_info', 'stack_info', 'stacklevel', 'extra'
        )}
        if extra_kwargs:
            msg = msg + " " + " ".join(f"{k}={v}" for k, v in extra_kwargs.items())
            for k in extra_kwargs:
                kwargs.pop(k)
        return msg, kwargs


@lru_cache(maxsize=128)
def get_logger(name: str) -> StructlogAdapter:
    """Get a logger for a module — cached for performance."""
    logger = logging.getLogger(name)
    return StructlogAdapter(logger, {})
