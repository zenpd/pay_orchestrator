from __future__ import annotations
from langgraph.graph import StateGraph, END
from agents.state import PaymentState
from agents.guardrails import guardrails_node
from agents.nodes.context_collector import context_collector_node
from agents.nodes.policy_reasoner import policy_reasoner_node
from agents.nodes.optimizer import optimizer_node
from agents.nodes.layer4_validation import layer4_validation_node
from agents.nodes.execution import execution_node
from agents.nodes.layer4_update import layer4_update_node
from agents.nodes.feedback import feedback_node
from shared.logger import get_logger

log = get_logger("agents.graph")


def _compliance_router(state: PaymentState) -> str:
    """Route after policy_reasoner based on compliance_status."""
    status = state.get("compliance_status", "HOLD_FOR_REVIEW")
    if status == "APPROVED":
        return "approved"
    if status == "REJECTED":
        log.warning("compliance_rejected", notes=state.get("compliance_notes"), payment_id=state.get("payment_id"))
        return "rejected"
    log.info("compliance_hold", notes=state.get("compliance_notes"), payment_id=state.get("payment_id"))
    return "hold"


def _layer4_router(state: PaymentState) -> str:
    """Route after layer4_validation based on layer4_validation_status."""
    if state.get("layer4_validation_status") == "APPROVED":
        return "approved"
    log.warning("layer4_rejected", payment_id=state.get("payment_id"))
    return "rejected"


def _guardrails_router(state: PaymentState) -> str:
    """Abort immediately if guardrails detected an injection."""
    if state.get("error"):
        return "blocked"
    return "ok"


def build_graph() -> StateGraph:
    workflow = StateGraph(PaymentState)

    # ── Nodes ──────────────────────────────────────────────────────────────
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("context_collector", context_collector_node)
    workflow.add_node("policy_reasoner", policy_reasoner_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("layer4_validation", layer4_validation_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("layer4_update", layer4_update_node)
    workflow.add_node("feedback", feedback_node)

    # ── Entry ──────────────────────────────────────────────────────────────
    workflow.set_entry_point("guardrails")

    # ── Edges ──────────────────────────────────────────────────────────────
    workflow.add_conditional_edges(
        "guardrails",
        _guardrails_router,
        {"ok": "context_collector", "blocked": END},
    )
    workflow.add_edge("context_collector", "policy_reasoner")
    workflow.add_conditional_edges(
        "policy_reasoner",
        _compliance_router,
        {"approved": "optimizer", "rejected": END, "hold": END},
    )
    workflow.add_edge("optimizer", "layer4_validation")
    workflow.add_conditional_edges(
        "layer4_validation",
        _layer4_router,
        {"approved": "execution", "rejected": END},
    )
    workflow.add_edge("execution", "layer4_update")
    workflow.add_edge("layer4_update", "feedback")
    workflow.add_edge("feedback", END)

    return workflow


compiled_graph = build_graph().compile()
