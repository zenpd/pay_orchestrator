"""LangGraph payment orchestration workflow."""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from typing import Literal
import uuid
from datetime import datetime

from agents.state import PaymentState, PaymentRequest, RailType, RailScore
from services.regional_data import (
    get_rails_for_region,
    get_corridors_for_region,
    score_rail_for_request,
    Region
)
from shared.logger import get_logger

log = get_logger("workflows.payment")


def node_analyze_payment(state: PaymentState) -> PaymentState:
    """Validate and analyze the payment request."""
    log.info(f"analyze_payment: session={state.session_id}")
    
    req = state.payment_request
    errors = []
    
    # Validation
    if req.amount <= 0:
        errors.append("Amount must be positive")
    if not req.sender_id or not req.receiver_id:
        errors.append("Sender and receiver IDs required")
    if not req.corridor:
        errors.append("Corridor (e.g., ZA_US) required")
    
    state.errors.extend(errors)
    state.stage = "analyzing"
    state.messages.append(f"Payment analyzed: amount={req.amount} {req.currency}, corridor={req.corridor}")
    
    if errors:
        state.stage = "failed"
        return state
    
    state.stage = "scoring"
    return state


# Map rail names to RailType enums (best effort; multiple rails may share a type but
# rail_scores_dict uses string keys, avoiding any collision).
_RAIL_TYPE_MAP: dict = {
    "ACH": RailType.BATCH_ACH,
    "Wire_Transfer": RailType.SWIFT_GPI,
    "RealTimePayments": RailType.NAMPAY,
    "SWIFT_International": RailType.SWIFT_GPI,
    "Remittance_Services": RailType.PARTNER_NETWORK,
    "Faster_Payments": RailType.NAMPAY,
    "BACS": RailType.BATCH_ACH,
    "CHAPS": RailType.RTGS_BULK,
    "SWIFT_GPI": RailType.SWIFT_GPI,
    "RTGS": RailType.RTGS_BULK,
    "PayShap_Instant": RailType.NAMPAY,
    "EFT": RailType.BATCH_ACH,
    "Remittance": RailType.PARTNER_NETWORK,
    "SEPA_Instant": RailType.NAMPAY,
    "SEPA_Standard": RailType.BATCH_ACH,
    "CHIPS": RailType.PARTNER_NETWORK,
}


def node_score_rails(state: PaymentState) -> PaymentState:
    """Evaluate and score all available payment rails for the region."""
    log.info(f"score_rails: session={state.session_id}")

    req = state.payment_request
    region = state.region or "US"

    try:
        regional_rails = get_rails_for_region(region)
        corridors = get_corridors_for_region(region)

        # Accept corridor as either a corridor code key (e.g. "US_UK") or a value
        # (e.g. "USA → United Kingdom") so the frontend/backend are never out-of-sync.
        corridor_code = req.corridor
        if req.corridor not in corridors:
            # Try matching against corridor values
            reverse_map = {v: k for k, v in corridors.items()}
            corridor_code = reverse_map.get(req.corridor)
            if corridor_code is None:
                state.errors.append(f"Corridor '{req.corridor}' not available in {region}")
                state.messages.append(f"Available corridors: {', '.join(corridors.keys())}")
                state.stage = "failed"
                return state

        # Score each rail and store in rail_scores_dict (string-keyed, no collisions)
        for rail_name, rail_data in regional_rails.items():
            composite_score = score_rail_for_request(rail_data, req.amount, corridor_code)

            if composite_score == 0:
                reason = "Ineligible for this transaction"
                if req.amount > rail_data["max_amount"]:
                    reason = f"Amount exceeds limit (max: ${rail_data['max_amount']:,.0f})"
                elif req.amount < rail_data["min_amount"]:
                    reason = f"Amount below minimum (min: ${rail_data['min_amount']:,.0f})"
                state.messages.append(f"Rail {rail_name}: {reason}")
                continue

            rail_type = _RAIL_TYPE_MAP.get(rail_name, RailType.SWIFT_GPI)
            feasibility = "FEASIBLE" if rail_data["success_rate"] > 0.9 else "RISKY"

            # Canonical dict-based storage (string keys, preserves every rail)
            state.rail_scores_dict[rail_name] = {
                "rail_type": rail_type.value,
                "composite_score": composite_score,
                "cost_score": rail_data["cost_score"],
                "speed_score": rail_data["speed_score"],
                "reliability_score": rail_data["reliability_score"],
                "estimated_cost_usd": rail_data["estimated_cost_usd"],
                "estimated_time_hours": rail_data["estimated_time_hours"],
                "feasibility": feasibility,
            }

            state.messages.append(
                f"Rail {rail_name}: score={composite_score:.1f}, cost=${rail_data['estimated_cost_usd']:.2f}"
            )

    except Exception as e:
        state.errors.append(f"Error scoring rails: {str(e)}")
        log.error(f"Error in node_score_rails: {str(e)}")
        state.stage = "failed"
        return state

    if not state.rail_scores_dict:
        state.errors.append("No eligible rails found for this payment")
        state.stage = "failed"
        return state

    state.stage = "deciding"
    return state


def node_select_rail(state: PaymentState) -> PaymentState:
    """Select the best payment rail based on scores."""
    log.info(f"select_rail: session={state.session_id}")

    if not state.rail_scores_dict:
        state.errors.append("No eligible rails found")
        state.stage = "failed"
        return state

    # Pick rail with highest composite score (string-keyed dict avoids collisions)
    best_name = max(state.rail_scores_dict, key=lambda k: state.rail_scores_dict[k]["composite_score"])
    best_data = state.rail_scores_dict[best_name]
    state.selected_rail_name = best_name
    state.selected_rail = RailType(best_data["rail_type"])
    state.messages.append(
        f"Selected rail: {best_name} (type={best_data['rail_type']}, score={best_data['composite_score']:.1f})"
    )

    state.stage = "executing"
    return state


def node_execute_payment(state: PaymentState) -> PaymentState:
    """Execute the payment using the selected rail."""
    log.info(f"execute_payment: session={state.session_id}, rail={state.selected_rail}")
    
    if not state.selected_rail:
        state.errors.append("No rail selected for execution")
        state.stage = "failed"
        return state
    
    # Mock execution
    state.execution_result = {
        "transaction_id": str(uuid.uuid4()),
        "rail_used": state.selected_rail.value,
        "amount": state.payment_request.amount,
        "currency": state.payment_request.currency,
        "status": "SUBMITTED",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state.messages.append(f"Payment executed: txn_id={state.execution_result['transaction_id']}")
    state.stage = "completed"
    
    return state


def _get_attr(state, key, default=None):
    """Safely read from state whether it's a dataclass or a dict."""
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def router_analyze(state) -> Literal["score", "failed"]:
    """Route after analysis: proceed to scoring unless there are errors."""
    errors = _get_attr(state, "errors", [])
    return "score" if not errors else "failed"


def router_to_execute(state) -> Literal["execute", "failed"]:
    """Route after rail selection."""
    if _get_attr(state, "selected_rail"):
        return "execute"
    return "failed"


def node_failed(state: PaymentState) -> PaymentState:
    """Handle workflow failure."""
    state.stage = "failed"
    log.error(f"Workflow failed: session={state.session_id}, errors={state.errors}")
    return state


# Build the workflow graph
workflow = StateGraph(PaymentState)

# Add nodes
workflow.add_node("analyze", node_analyze_payment)
workflow.add_node("score", node_score_rails)
workflow.add_node("select", node_select_rail)
workflow.add_node("execute", node_execute_payment)
workflow.add_node("failed", node_failed)

# Add edges
workflow.add_edge(START, "analyze")
workflow.add_conditional_edges("analyze", router_analyze)
workflow.add_edge("score", "select")
workflow.add_conditional_edges("select", router_to_execute)
workflow.add_edge("execute", END)
workflow.add_edge("failed", END)

# Compile the graph
payment_orchestration_graph = workflow.compile()
