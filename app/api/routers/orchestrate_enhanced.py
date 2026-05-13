"""
Enhanced payment orchestration router with decision justification.
Provides endpoints for agentic payment orchestration with rich decision reasoning.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.state import PaymentState, PaymentRequest
from workflows.payment_enhanced import payment_orchestration_graph_enhanced
from services.regional_data import (
    get_rails_for_region,
    get_corridors_for_region,
    get_currencies_for_region,
)
from shared.logger import get_logger

log = get_logger("api.routers.orchestrate_enhanced")
router = APIRouter()


# Enhanced Schemas with Decision Justification
class RailScoreDetailSchema(BaseModel):
    """Detailed rail score with all metrics."""
    name: str
    composite_score: float
    cost_score: float
    speed_score: float
    reliability_score: float
    estimated_cost_usd: float
    estimated_time_hours: float
    success_rate: float
    availability: float
    compliance_tier: str
    ineligibility_reason: Optional[str] = None


class ComplianceResultSchema(BaseModel):
    """Compliance validation result."""
    status: str  # APPROVED, HOLD_FOR_REVIEW, REJECTED
    risk_score: float
    checks: Dict[str, bool]
    risk_factors: list
    notes: str
    warnings: list


class DecisionJustificationSchema(BaseModel):
    """Complete decision justification."""
    selected_rail: str
    backup_rail: Optional[str]
    total_score: float
    score_breakdown: Dict[str, float]
    cost_analysis: str
    speed_analysis: str
    reliability_analysis: str
    compliance_considerations: str
    business_rules_applied: list
    decision_reasoning: str
    comparative_analysis: Dict[str, Dict[str, Any]]


class EnhancedPaymentResponseSchema(BaseModel):
    """Enhanced response with full decision justification."""
    session_id: str
    stage: str
    transaction_status: str
    
    # Decision justification
    decision_justification: Optional[DecisionJustificationSchema]
    compliance_result: Optional[ComplianceResultSchema]
    
    # Rail details
    selected_rail: Optional[str]
    rail_scores: Dict[str, RailScoreDetailSchema]
    
    # Execution
    execution_result: Optional[Dict[str, Any]]
    
    # Workflow
    messages: list = Field(default_factory=list)
    errors: list = Field(default_factory=list)
    created_at: datetime


@router.post("/orchestrate/enhanced", response_model=EnhancedPaymentResponseSchema)
async def orchestrate_payment_enhanced(request: "PaymentRequestSchema") -> EnhancedPaymentResponseSchema:
    """
    Orchestrate payment with complete decision justification.
    
    Enhanced workflow integrating:
    - PolicyReasonerAgent: Compliance validation
    - ContextCollectorAgent: Payment contextualization
    - OptimizerAgent: Multi-objective rail selection with detailed reasoning
    
    The workflow:
    1. Collect and contextualize payment information
    2. Validate compliance using regulatory rules
    3. Validate and analyze payment request
    4. Score all eligible payment rails
    5. Optimize and justify rail selection
    6. Execute the payment
    
    Returns:
    - Complete decision justification showing why rail was selected
    - Comparative analysis of all evaluated rails
    - Compliance validation results
    - Business rules applied
    - Step-by-step messages and any errors
    """
    session_id = str(uuid.uuid4())
    log.info(
        f"orchestrate_payment_enhanced: session={session_id}, "
        f"amount=${request.amount:,.2f} {request.currency}"
    )

    try:
        # Initialize payment request
        payment_request = PaymentRequest(
            session_id=session_id,
            amount=request.amount,
            currency=request.currency,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            corridor=request.corridor or "",
            region=request.region or "US",
            deadline_minutes=request.deadline_minutes,
            metadata=request.metadata or {},
        )

        # Initialize state
        state = PaymentState(
            session_id=session_id,
            payment_request=payment_request,
            region=request.region or "US",
            stage="initializing",
            created_at=datetime.utcnow().isoformat(),
        )

        # Run enhanced workflow
        final_state = payment_orchestration_graph_enhanced.invoke(state)

        # Format rail scores
        rail_scores_response = {
            rail_name: RailScoreDetailSchema(**rail_data)
            for rail_name, rail_data in final_state.rail_scores_dict.items()
        }

        # Format compliance result
        compliance_schema = None
        if final_state.compliance_result:
            compliance_schema = ComplianceResultSchema(**final_state.compliance_result)

        # Format decision justification
        justification_schema = None
        if final_state.decision_justification:
            justification_schema = DecisionJustificationSchema(**final_state.decision_justification)

        # Determine transaction status
        transaction_status = "completed" if final_state.stage == "completed" else final_state.stage

        response = EnhancedPaymentResponseSchema(
            session_id=session_id,
            stage=final_state.stage,
            transaction_status=transaction_status,
            decision_justification=justification_schema,
            compliance_result=compliance_schema,
            selected_rail=final_state.selected_rail_name,
            rail_scores=rail_scores_response,
            execution_result=final_state.execution_result,
            messages=final_state.messages,
            errors=final_state.errors,
            created_at=datetime.fromisoformat(final_state.created_at) if final_state.created_at else datetime.utcnow(),
        )

        log.info(
            f"orchestrate_payment_enhanced completed: session={session_id}, "
            f"status={transaction_status}, rail={final_state.selected_rail_name}"
        )

        return response

    except Exception as e:
        log.error(f"orchestrate_payment_enhanced failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Payment orchestration failed: {str(e)}"
        )


@router.get("/decision-matrix/{region}")
async def get_decision_matrix(region: str) -> Dict[str, Any]:
    """
    Get decision matrix template for a region.
    Shows the criteria used for rail selection optimization.
    """
    try:
        rails = get_rails_for_region(region)
        
        # Build decision matrix
        matrix = {
            "region": region,
            "optimization_criteria": {
                "cost": {
                    "weight": 0.30,
                    "description": "Transaction cost efficiency",
                    "optimal_range": "$0 - $50"
                },
                "speed": {
                    "weight": 0.25,
                    "description": "Processing time",
                    "optimal_range": "< 4 hours"
                },
                "reliability": {
                    "weight": 0.30,
                    "description": "Success rate and availability",
                    "optimal_range": "> 95%"
                },
                "compliance": {
                    "weight": 0.15,
                    "description": "Regulatory compliance tier",
                    "optimal_range": "Premium/Standard"
                }
            },
            "business_rules": {
                "high_value_rule": {
                    "threshold": "$100,000",
                    "applies_to": "High-value transactions",
                    "action": "Boost reliability score by 15%"
                },
                "urgent_rule": {
                    "threshold": "< 4 hours deadline",
                    "applies_to": "Time-sensitive payments",
                    "action": "Boost speed score by 25%"
                },
                "cost_sensitive_rule": {
                    "threshold": "< $1,000",
                    "applies_to": "Low-amount transactions",
                    "action": "Boost cost score by 20%"
                }
            },
            "available_rails": {
                name: {
                    "cost_score": rail["cost_score"],
                    "speed_score": rail["speed_score"],
                    "reliability_score": rail["reliability_score"],
                    "estimated_cost_usd": rail["estimated_cost_usd"],
                    "estimated_time_hours": rail["estimated_time_hours"],
                    "success_rate": rail["success_rate"]
                }
                for name, rail in rails.items()
            }
        }
        
        return matrix
        
    except Exception as e:
        log.error(f"Error getting decision matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-matrix/{region}")
async def get_compliance_matrix(region: str) -> Dict[str, Any]:
    """
    Get compliance validation matrix for a region.
    Shows regulatory checks and requirements by region.
    """
    compliance_matrices = {
        "US": {
            "region": "US",
            "transaction_limits": {
                "max_amount": 100000,
                "description": "Maximum per-transaction limit"
            },
            "required_checks": [
                "OFAC Sanctions Screening",
                "AML Verification",
                "Purpose Code",
                "Tax ID Verification",
                "FinCEN Reporting"
            ],
            "high_risk_factors": [
                "Sanctioned countries",
                "High transaction amount",
                "Complex corridor",
                "Suspicious purpose"
            ]
        },
        "UK": {
            "region": "UK",
            "transaction_limits": {
                "max_amount": 150000,
                "description": "Maximum per-transaction limit"
            },
            "required_checks": [
                "OFAC Sanctions Screening",
                "AML Verification",
                "FCA Compliance",
                "HMRC Reporting"
            ],
            "high_risk_factors": [
                "OFAC-sanctioned jurisdictions",
                "High transaction amount",
                "Correspondent banking"
            ]
        },
        "SA": {
            "region": "SA",
            "transaction_limits": {
                "max_amount": 1000000,
                "description": "Maximum per-transaction limit"
            },
            "required_checks": [
                "SARB Compliance",
                "Exchange Control Regulations",
                "Purpose Code",
                "Beneficial Owner Verification"
            ],
            "high_risk_factors": [
                "High transaction amount",
                "Restricted corridors",
                "Non-resident accounts"
            ]
        },
        "EUR": {
            "region": "EUR",
            "transaction_limits": {
                "max_amount": 50000,
                "description": "Maximum per-transaction limit for SEPA"
            },
            "required_checks": [
                "OFAC Sanctions Screening",
                "GDPR Compliance",
                "PSD2 Authentication",
                "ECB Monitoring"
            ],
            "high_risk_factors": [
                "Third-country beneficiary",
                "High transaction amount",
                "FATF Grey List Countries"
            ]
        }
    }
    
    if region not in compliance_matrices:
        raise HTTPException(
            status_code=404,
            detail=f"Compliance matrix not found for region: {region}"
        )
    
    return compliance_matrices[region]
