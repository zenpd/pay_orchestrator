"""
Enhanced payment orchestration workflow with agent-based decision justification.
Integrates PolicyReasoner, ContextCollector, and Optimizer agents.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from typing import Literal, Optional, Dict, Any
import uuid
from datetime import datetime

from agents.state import PaymentState, PaymentRequest, RailType, RailScore
from agents.policy_reasoner import PolicyReasonerAgent, ComplianceResult
from agents.optimizer import OptimizerAgent, RailDecisionJustification
from agents.context_collector import ContextCollectorAgent, PaymentContext
from services.regional_data import (
    get_rails_for_region,
    get_corridors_for_region,
    score_rail_for_request,
    Region
)
from shared.logger import get_logger

log = get_logger("workflows.payment_enhanced")

# Initialize agents
policy_reasoner = PolicyReasonerAgent()
optimizer = OptimizerAgent()
context_collector = ContextCollectorAgent()


def node_collect_context(state: PaymentState) -> PaymentState:
    """Collect and contextualize payment information."""
    log.info(f"collect_context: session={state.session_id}")
    
    req = state.payment_request
    region = state.region or "US"
    
    try:
        # Get regional data
        regional_rails = get_rails_for_region(region)
        corridors = get_corridors_for_region(region)
        
        # Collect context
        context = context_collector.collect_and_contextualize(
            amount=req.amount,
            currency=req.currency,
            sender_country=region,
            receiver_country="US",  # TODO: parse from corridor
            corridor=req.corridor or "",
            deadline_hours=req.deadline_minutes / 60 if req.deadline_minutes else None,
            available_rails=regional_rails,
            compliance_risk=0.1,  # Will be updated by compliance check
            rail_scores=None
        )
        
        state.decision_context = context
        state.messages.append(f"Context collected: {context.transaction_type} transaction, score={context.transaction_score:.1%}")
        state.stage = "context_collected"
        
    except Exception as e:
        state.errors.append(f"Error collecting context: {str(e)}")
        log.error(f"Error in node_collect_context: {str(e)}")
        state.stage = "failed"
    
    return state


def node_validate_compliance(state: PaymentState) -> PaymentState:
    """Validate payment compliance using PolicyReasonerAgent."""
    log.info(f"validate_compliance: session={state.session_id}")
    
    req = state.payment_request
    
    try:
        # Run compliance validation
        compliance_result = policy_reasoner.validate_payment_compliance(
            amount=req.amount,
            currency=req.currency,
            sender_country=state.region or "US",
            receiver_country="US",  # TODO: parse from corridor
            corridor=req.corridor or "",
            sender_name=getattr(req, 'sender_name', None),
            receiver_name=getattr(req, 'receiver_name', None)
        )
        
        state.compliance_result = {
            "status": compliance_result.status,
            "risk_score": compliance_result.risk_score,
            "checks": compliance_result.compliance_checks,
            "risk_factors": compliance_result.risk_factors,
            "notes": compliance_result.compliance_notes,
            "warnings": compliance_result.warnings
        }
        
        state.messages.append(
            f"Compliance check: {compliance_result.status} (risk={compliance_result.risk_score:.1%})"
        )
        
        # Update decision context with compliance info
        if state.decision_context:
            state.decision_context.is_high_risk = compliance_result.risk_score >= 0.5
        
        # Continue only if not rejected
        if compliance_result.status == "REJECTED":
            state.errors.append(f"Compliance rejected: {compliance_result.compliance_notes}")
            state.stage = "failed"
            return state
        
        state.stage = "compliance_validated"
        
    except Exception as e:
        state.errors.append(f"Error validating compliance: {str(e)}")
        log.error(f"Error in node_validate_compliance: {str(e)}")
        state.stage = "failed"
    
    return state


def node_analyze_payment(state: PaymentState) -> PaymentState:
    """Basic payment validation and analysis."""
    log.info(f"analyze_payment: session={state.session_id}")
    
    req = state.payment_request
    errors = []
    
    # Validation
    if req.amount <= 0:
        errors.append("Amount must be positive")
    if not req.sender_id or not req.receiver_id:
        errors.append("Sender and receiver IDs required")
    if not req.corridor:
        errors.append("Corridor (e.g., US_UK) required")
    
    state.errors.extend(errors)
    state.stage = "analyzing"
    state.messages.append(f"Payment analyzed: ${req.amount:,.2f} {req.currency}, corridor={req.corridor}")
    
    if errors:
        state.stage = "failed"
        return state
    
    state.stage = "analyzed"
    return state


def node_score_rails_enhanced(state: PaymentState) -> PaymentState:
    """Evaluate and score payment rails using regional data."""
    log.info(f"score_rails_enhanced: session={state.session_id}")
    
    req = state.payment_request
    region = state.region or "US"
    
    try:
        # Get regional rails and corridors
        regional_rails = get_rails_for_region(region)
        corridors = get_corridors_for_region(region)
        
        # Validate corridor
        if req.corridor and req.corridor not in corridors:
            state.errors.append(f"Corridor '{req.corridor}' not available in {region}")
            state.messages.append(f"Available corridors: {', '.join(corridors.keys())}")
            state.stage = "failed"
            return state
        
        # Score each rail
        rail_scores_dict = {}
        eligible_count = 0
        
        for rail_name, rail_data in regional_rails.items():
            # Calculate composite score
            composite_score = score_rail_for_request(rail_data, req.amount, req.corridor or "")
            
            if composite_score == 0:
                reason = "Ineligible for this transaction"
                if req.amount > rail_data.get("max_amount", float('inf')):
                    reason = f"Amount exceeds limit (max: ${rail_data.get('max_amount', 0):,.0f})"
                elif req.amount < rail_data.get("min_amount", 0):
                    reason = f"Amount below minimum (min: ${rail_data.get('min_amount', 0):,.0f})"
                state.messages.append(f"Rail {rail_name}: ❌ {reason}")
                continue
            
            eligible_count += 1
            rail_scores_dict[rail_name] = {
                "name": rail_name,
                "composite_score": composite_score,
                "cost_score": rail_data.get("cost_score", 50),
                "speed_score": rail_data.get("speed_score", 50),
                "reliability_score": rail_data.get("reliability_score", 80),
                "estimated_cost_usd": rail_data.get("estimated_cost_usd", 0),
                "estimated_time_hours": rail_data.get("estimated_time_hours", 24),
                "success_rate": rail_data.get("success_rate", 0.95),
                "availability": rail_data.get("availability", 0.99),
                "compliance_tier": rail_data.get("compliance_tier", "standard"),
                "min_amount": rail_data.get("min_amount", 0),
                "max_amount": rail_data.get("max_amount", float('inf'))
            }
            
            state.messages.append(
                f"Rail {rail_name}: ✓ score={composite_score:.1f}, "
                f"${rail_data.get('estimated_cost_usd', 0):.2f}, "
                f"{rail_data.get('estimated_time_hours', 24):.1f}h"
            )
        
        if not rail_scores_dict:
            state.errors.append("No eligible rails found for this payment")
            state.stage = "failed"
            return state
        
        state.rail_scores_dict = rail_scores_dict
        state.messages.append(f"Scored {eligible_count} eligible rails for {region}")
        state.stage = "rails_scored"
        
    except Exception as e:
        state.errors.append(f"Error scoring rails: {str(e)}")
        log.error(f"Error in node_score_rails_enhanced: {str(e)}")
        state.stage = "failed"
    
    return state


def node_optimize_and_justify(state: PaymentState) -> PaymentState:
    """Select optimal rail with detailed decision justification using OptimizerAgent."""
    log.info(f"optimize_and_justify: session={state.session_id}")
    
    req = state.payment_request
    
    try:
        if not hasattr(state, 'rail_scores_dict') or not state.rail_scores_dict:
            state.errors.append("No rails scored for optimization")
            state.stage = "failed"
            return state
        
        # Get compliance risk (default to 0.1 if not available)
        compliance_risk = 0.1
        if state.compliance_result:
            compliance_risk = state.compliance_result.get("risk_score", 0.1)
        
        # Run optimizer agent
        justification = optimizer.optimize_and_justify(
            rails_data=state.rail_scores_dict,
            amount=req.amount,
            deadline_hours=req.deadline_minutes / 60 if req.deadline_minutes else None,
            region=state.region or "US",
            compliance_risk=compliance_risk
        )
        
        state.decision_justification = {
            "selected_rail": justification.selected_rail,
            "backup_rail": justification.backup_rail,
            "total_score": justification.total_score,
            "score_breakdown": justification.score_breakdown,
            "cost_analysis": justification.cost_analysis,
            "speed_analysis": justification.speed_analysis,
            "reliability_analysis": justification.reliability_analysis,
            "compliance_considerations": justification.compliance_considerations,
            "business_rules_applied": justification.business_rules_applied,
            "decision_reasoning": justification.decision_reasoning,
            "comparative_analysis": justification.comparative_analysis
        }
        
        state.selected_rail_name = justification.selected_rail
        state.messages.append(
            f"✨ Optimized selection: {justification.selected_rail} "
            f"(score={justification.total_score:.1f})"
        )
        state.messages.append(f"Decision: {justification.decision_reasoning}")
        
        state.stage = "optimized"
        
    except Exception as e:
        state.errors.append(f"Error in optimization: {str(e)}")
        log.error(f"Error in node_optimize_and_justify: {str(e)}")
        state.stage = "failed"
    
    return state


def node_execute_payment(state: PaymentState) -> PaymentState:
    """Execute the payment using the selected rail."""
    log.info(f"execute_payment: session={state.session_id}, rail={state.selected_rail_name}")
    
    if not state.selected_rail_name:
        state.errors.append("No rail selected for execution")
        state.stage = "failed"
        return state
    
    try:
        # Mock execution
        rail_data = state.rail_scores_dict.get(state.selected_rail_name, {})
        
        state.execution_result = {
            "transaction_id": str(uuid.uuid4()),
            "rail_used": state.selected_rail_name,
            "amount": state.payment_request.amount,
            "currency": state.payment_request.currency,
            "status": "SUBMITTED",
            "timestamp": datetime.utcnow().isoformat(),
            "estimated_cost": rail_data.get("estimated_cost_usd", 0),
            "estimated_time_hours": rail_data.get("estimated_time_hours", 24),
            "justification_summary": state.decision_justification or {}
        }
        
        state.messages.append(
            f"✅ Payment executed: txn_id={state.execution_result['transaction_id']}, "
            f"rail={state.selected_rail_name}"
        )
        state.stage = "completed"
        
    except Exception as e:
        state.errors.append(f"Error executing payment: {str(e)}")
        log.error(f"Error in node_execute_payment: {str(e)}")
        state.stage = "failed"
    
    return state


def node_failed(state: PaymentState) -> PaymentState:
    """Handle workflow failure."""
    state.stage = "failed"
    state.messages.append("❌ Workflow failed")
    log.error(f"Workflow failed: session={state.session_id}, errors={state.errors}")
    return state


# Enhanced workflow graph
enhanced_workflow = StateGraph(PaymentState)

# Add nodes
enhanced_workflow.add_node("collect_context", node_collect_context)
enhanced_workflow.add_node("validate_compliance", node_validate_compliance)
enhanced_workflow.add_node("analyze", node_analyze_payment)
enhanced_workflow.add_node("score_rails", node_score_rails_enhanced)
enhanced_workflow.add_node("optimize_justify", node_optimize_and_justify)
enhanced_workflow.add_node("execute", node_execute_payment)
enhanced_workflow.add_node("failed", node_failed)

# Add edges (workflow sequence)
enhanced_workflow.add_edge(START, "collect_context")
enhanced_workflow.add_edge("collect_context", "analyze")
enhanced_workflow.add_conditional_edges(
    "analyze",
    lambda s: "validate_compliance" if not s.errors else "failed"
)
enhanced_workflow.add_conditional_edges(
    "validate_compliance",
    lambda s: "score_rails" if s.stage != "failed" else "failed"
)
enhanced_workflow.add_conditional_edges(
    "score_rails",
    lambda s: "optimize_justify" if s.stage != "failed" else "failed"
)
enhanced_workflow.add_conditional_edges(
    "optimize_justify",
    lambda s: "execute" if s.stage != "failed" else "failed"
)
enhanced_workflow.add_edge("execute", END)
enhanced_workflow.add_edge("failed", END)

# Compile the enhanced workflow
payment_orchestration_graph_enhanced = enhanced_workflow.compile()
