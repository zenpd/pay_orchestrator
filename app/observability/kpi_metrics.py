from __future__ import annotations
from opentelemetry import metrics as otel_metrics
from opentelemetry.sdk.metrics import MeterProvider
from shared.logger import get_logger

log = get_logger("observability.kpi_metrics")
_meter = otel_metrics.get_meter("pay_orchestrator")

payment_counter = _meter.create_counter(
    "payments_total",
    description="Total number of payment requests processed",
)
compliance_counter = _meter.create_counter(
    "compliance_decisions_total",
    description="Compliance decisions by status",
)
rail_usage_counter = _meter.create_counter(
    "rail_usage_total",
    description="Payment rail usage counts",
)
execution_histogram = _meter.create_histogram(
    "payment_execution_seconds",
    description="Payment execution time in seconds",
)


def record_payment(status: str, rail: str, execution_time: float) -> None:
    payment_counter.add(1, {"status": status, "rail": rail})
    execution_histogram.record(execution_time, {"rail": rail})
    rail_usage_counter.add(1, {"rail": rail})


def record_compliance(decision: str) -> None:
    compliance_counter.add(1, {"decision": decision})
