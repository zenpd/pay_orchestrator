from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class PaymentResponse(BaseModel):
    payment_id: str
    state_key: str
    compliance_status: str
    risk_score: float
    selected_rail: str
    backup_rail: str
    execution_status: str
    optimization_reasoning: str | None = None
    validation_violations: list[str] = []
    validation_warnings: list[str] = []
    fraud_check_score: float | None = None
    sanctions_check_status: str | None = None
    actual_cost: float | None = None
    actual_processing_time: float | None = None
    message_conversion: dict[str, Any] | None = None
    selection_details: dict[str, Any] | None = None
    error: str | None = None


class PaymentStatusResponse(BaseModel):
    payment_id: str
    state_key: str
    compliance_status: str | None = None
    execution_status: str | None = None
    selected_rail: str | None = None
    success: bool | None = None


class SessionMetricsResponse(BaseModel):
    total_payments: int
    successful_payments: int
    failed_payments: int
    success_rate_pct: float
    compliance_approvals: int
    compliance_rejections: int
    compliance_holds: int
    rails_used: dict[str, int]
    preference_counts: dict[str, int]


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    service: str = "pay-orchestrator"
