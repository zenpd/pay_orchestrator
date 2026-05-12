from __future__ import annotations
from typing import Annotated, Sequence, TypedDict
import operator
from langchain_core.messages import BaseMessage


class PaymentState(TypedDict, total=False):
    """
    LangGraph state for the payment orchestration workflow.
    Every field is optional (total=False) so nodes only patch what they produce.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    state_key: str          # "{payment_id}:{session_id}" composite key
    payment_id: str

    # ── Input (Layer 1) ───────────────────────────────────────────────────────
    amount: float
    currency_from: str
    currency_to: str
    sender_country: str
    receiver_country: str
    payment_purpose: str
    sender_name: str
    receiver_name: str
    routing_preference: str   # "fastest" | "cheapest" | "balanced"
    urgency: int              # 1–10
    risk_tolerance: int       # 1–10

    # ── Context enrichment (Agent 1 — ContextCollector) ───────────────────────
    fx_rate: float
    fx_rate_details: dict
    corridor_metadata: dict
    rail_performance: dict
    predicted_processing_times: dict
    validation_rules: dict

    # ── Compliance & Pre-validation (Agent 2 — PolicyReasoner) ────────────────
    compliance_status: str    # "APPROVED" | "HOLD_FOR_REVIEW" | "REJECTED"
    risk_score: float
    aml_cleared: bool
    sanctions_cleared: bool
    compliance_notes: str
    compliance_details: dict
    validation_violations: list[str]
    validation_warnings: list[str]
    fraud_check_score: float
    sanctions_check_status: str

    # ── Optimisation (Agent 3 — Optimizer) ────────────────────────────────────
    selected_rail: str
    backup_rail: str
    routing_score: dict
    optimization_reasoning: str

    # ── Layer 4 validation ────────────────────────────────────────────────────
    layer4_balance_check: dict
    layer4_account_status: dict
    layer4_validation_status: str   # "APPROVED" | "REJECTED"
    layer4_validation_details: dict

    # ── Execution (Agent 4) ───────────────────────────────────────────────────
    execution_status: str    # "SUCCESS" | "FAILED"
    formatted_message: dict
    rail_response: dict
    execution_time: float
    original_message_format: str
    converted_message_format: str
    conversion_time_ms: float

    # ── Layer 4 updates ───────────────────────────────────────────────────────
    layer4_confirmation: dict
    layer4_reconciliation: dict

    # ── Feedback (Agent 5) ────────────────────────────────────────────────────
    actual_cost: float
    actual_processing_time: float
    success: bool
    feedback_notes: str
    performance_delta: dict

    # ── Workflow control ──────────────────────────────────────────────────────
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    error: str
