"""LangGraph payment orchestration workflow."""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from typing import Literal
import uuid
from datetime import datetime

from agents.state import PaymentState, PaymentRequest, RailType, RailScore
from agents.tools.rail_tools import check_rail_eligibility, estimate_cost, estimate_processing_time
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


def node_score_rails(state: PaymentState) -> PaymentState:
    """Evaluate and score all available payment rails."""
    log.info(f"score_rails: session={state.session_id}")
    
    req = state.payment_request
    rails = [RailType.SWIFT_GPI, RailType.NAMPAY, RailType.PARTNER_NETWORK,
             RailType.RTGS_BULK, RailType.BATCH_ACH, RailType.SLOW_BATCH]
    
    for rail in rails:
        # Check eligibility
        eligible_result = check_rail_eligibility(rail.value, req.amount, req.corridor)
        if not eligible_result.get("eligible"):
            state.messages.append(f"Rail {rail.value}: ineligible - {eligible_result.get('reason')}")
            continue
        
        # Calculate scores
        est_cost = estimate_cost(rail.value, req.amount)
        cost_score = max(0, 100 - (est_cost * 10))  # Mock cost scoring
        speed_score = [r for r in [RailType.SWIFT_GPI, RailType.NAMPAY, RailType.RTGS_BULK] 
                       if r == rail][0:1]
        speed_val = 85 if speed_score else 50  # Domestic slower
        
        composite = (cost_score * 0.3 + speed_val * 0.4 + 80 * 0.3)  # Weighted scoring
        
        score = RailScore(
            rail_type=rail,
            composite_score=composite,
            cost_score=cost_score,
            speed_score=speed_val,
            reliability_score=90,
            estimated_cost_usd=est_cost,
            estimated_time_hours=4.0 if speed_val < 50 else 1.0,
            feasibility="FEASIBLE"
        )
        state.rail_scores[rail] = score
        state.messages.append(f"Rail {rail.value}: score={composite:.1f}")
    
    state.stage = "deciding"
    return state


def node_select_rail(state: PaymentState) -> PaymentState:
    """Select the best payment rail based on scores."""
    log.info(f"select_rail: session={state.session_id}")
    
    if not state.rail_scores:
        state.errors.append("No eligible rails found")
        state.stage = "failed"
        return state
    
    # Select highest composite score
    best_rail = max(state.rail_scores.values(), key=lambda x: x.composite_score)
    state.selected_rail = best_rail.rail_type
    state.messages.append(f"Selected rail: {best_rail.rail_type.value} (score={best_rail.composite_score:.1f})")
    
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


def router_to_execute(state: PaymentState) -> Literal["node_execute_payment", "node_failed"]:
    """Route after rail selection."""
    if state.selected_rail:
        return "node_execute_payment"
    return "node_failed"


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
workflow.add_conditional_edges("analyze", lambda s: "score" if not s.errors else "failed")
workflow.add_edge("score", "select")
workflow.add_conditional_edges("select", router_to_execute)
workflow.add_edge("execute", END)
workflow.add_edge("failed", END)

# Compile the graph
payment_orchestration_graph = workflow.compile()
