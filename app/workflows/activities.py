"""
Temporal workflow activities for payment processing.
Each activity is a thin wrapper around the corresponding LangGraph agent node.
"""
from __future__ import annotations
from temporalio import activity
from agents.nodes.context_collector import context_collector_node
from agents.nodes.policy_reasoner import policy_reasoner_node
from agents.nodes.optimizer import optimizer_node
from agents.nodes.layer4_validation import layer4_validation_node
from agents.nodes.execution import execution_node
from agents.nodes.layer4_update import layer4_update_node
from agents.nodes.feedback import feedback_node
from agents.state import PaymentState


@activity.defn(name="collect_context")
async def collect_context(state: dict) -> dict:
    return context_collector_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="validate_policy")
async def validate_policy(state: dict) -> dict:
    return policy_reasoner_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="optimize_route")
async def optimize_route(state: dict) -> dict:
    return optimizer_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="validate_layer4")
async def validate_layer4(state: dict) -> dict:
    return layer4_validation_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="execute_payment")
async def execute_payment(state: dict) -> dict:
    return execution_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="update_layer4")
async def update_layer4(state: dict) -> dict:
    return layer4_update_node(PaymentState(**state))  # type: ignore[arg-type]


@activity.defn(name="record_feedback")
async def record_feedback(state: dict) -> dict:
    return feedback_node(PaymentState(**state))  # type: ignore[arg-type]
