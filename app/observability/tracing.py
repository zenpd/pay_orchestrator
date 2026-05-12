from __future__ import annotations
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from shared.config import get_settings
from shared.logger import get_logger

log = get_logger("observability.tracing")


def init_tracing() -> None:
    settings = get_settings()
    provider = TracerProvider()

    if settings.app_env != "development":
        try:
            exporter = OTLPSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(exporter))
            log.info("tracing.otlp_enabled")
        except Exception as exc:
            log.warning("tracing.otlp_failed", error=str(exc))

    trace.set_tracer_provider(provider)

    try:
        FastAPIInstrumentor().instrument()
    except Exception:
        pass
