"""Payment orchestration router."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from agents.state import PaymentState, PaymentRequest
from api.schemas import PaymentRequestSchema, PaymentResponseSchema, RailScoreSchema
from workflows.payment import payment_orchestration_graph
from services.regional_data import (
    get_rails_for_region,
    get_corridors_for_region,
    get_currencies_for_region,
)
from shared.logger import get_logger

log = get_logger("api.routers.orchestrate")
router = APIRouter()


@router.post("/orchestrate", response_model=PaymentResponseSchema)
async def orchestrate_payment(request: PaymentRequestSchema) -> PaymentResponseSchema:
    """Orchestrate payment across optimal rail selection.
    
    The workflow:
    1. Validates payment request
    2. Scores all eligible payment rails
    3. Selects the optimal rail
    4. Executes the payment
    
    Returns complete orchestration results including scores and execution details.
    """
    session_id = str(uuid.uuid4())
    log.info(f"orchestrate_payment: session={session_id}, amount={request.amount} {request.currency}")

    try:
        # Initialize state
        payment_request = PaymentRequest(
            session_id=session_id,
            amount=request.amount,
            currency=request.currency,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            corridor=request.corridor,
            region=request.region,  # Add region
            deadline_minutes=request.deadline_minutes,
            metadata=request.metadata,
        )

        state = PaymentState(
            session_id=session_id,
            payment_request=payment_request,
            region=request.region,  # Add region to state
            stage="initializing",
            created_at=datetime.utcnow().isoformat(),
        )

        # Invoke workflow — LangGraph may return a dict or a PaymentState dataclass
        raw = payment_orchestration_graph.invoke(state)

        # Normalise to plain values regardless of return type (dict vs dataclass)
        if isinstance(raw, dict):
            final_stage = raw.get("stage", "failed")
            rail_scores_dict: dict = raw.get("rail_scores_dict") or {}
            selected_rail_name: str | None = raw.get("selected_rail_name")
            selected_rail_enum = raw.get("selected_rail")
            final_execution_result = raw.get("execution_result")
            final_messages = raw.get("messages") or []
            final_errors = raw.get("errors") or []
            final_created_at = raw.get("created_at")
        else:
            final_stage = raw.stage
            rail_scores_dict = getattr(raw, "rail_scores_dict", {}) or {}
            selected_rail_name = getattr(raw, "selected_rail_name", None)
            selected_rail_enum = getattr(raw, "selected_rail", None)
            final_execution_result = raw.execution_result
            final_messages = raw.messages or []
            final_errors = raw.errors or []
            final_created_at = raw.created_at

        # Build rail scores response from the string-keyed dict (all rails preserved)
        rail_scores_response: dict = {}
        for rail_name, score_data in rail_scores_dict.items():
            if isinstance(score_data, dict):
                rail_scores_response[rail_name] = RailScoreSchema(
                    rail_type=score_data.get("rail_type", rail_name),
                    composite_score=score_data.get("composite_score", 0.0),
                    cost_score=score_data.get("cost_score", 0.0),
                    speed_score=score_data.get("speed_score", 0.0),
                    reliability_score=score_data.get("reliability_score", 0.0),
                    estimated_cost_usd=score_data.get("estimated_cost_usd", 0.0),
                    estimated_time_hours=score_data.get("estimated_time_hours", 0.0),
                    feasibility=score_data.get("feasibility", "UNKNOWN"),
                )

        # Resolve selected rail label (prefer human-readable name, fall back to enum value)
        if selected_rail_name:
            selected_rail_label = selected_rail_name
        elif selected_rail_enum is not None:
            selected_rail_label = (
                selected_rail_enum.value
                if hasattr(selected_rail_enum, "value")
                else str(selected_rail_enum)
            )
        else:
            selected_rail_label = None

        return PaymentResponseSchema(
            session_id=session_id,
            stage=final_stage,
            selected_rail=selected_rail_label,
            rail_scores=rail_scores_response,
            execution_result=final_execution_result,
            messages=final_messages,
            errors=final_errors,
            created_at=datetime.fromisoformat(final_created_at) if final_created_at else None,
        )

    except Exception as e:
        log.error(f"orchestrate_payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment orchestration failed: {str(e)}")


@router.get("/regions")
async def get_regions() -> dict:
    """Get available regions."""
    return {
        "regions": ["US", "UK", "SA", "EUR"],
        "descriptions": {
            "US": "United States",
            "UK": "United Kingdom",
            "SA": "South Africa",
            "EUR": "Europe",
        }
    }


@router.get("/regions/{region}/rails")
async def get_regional_rails(region: str) -> dict:
    """Get payment rails for a specific region with realistic data."""
    from services.regional_data import get_rails_for_region, get_corridors_for_region, get_currencies_for_region
    
    try:
        rails_dict = get_rails_for_region(region)
        corridors = get_corridors_for_region(region)
        currencies = get_currencies_for_region(region)
        
        # Format rails for frontend
        formatted_rails = {}
        for rail_name, rail_data in rails_dict.items():
            formatted_rails[rail_name] = {
                "name": rail_data["name"],
                "type": rail_data["type"],
                "speed_score": rail_data["speed_score"],
                "cost_score": rail_data["cost_score"],
                "reliability_score": rail_data["reliability_score"],
                "estimated_cost_usd": rail_data["estimated_cost_usd"],
                "estimated_time_hours": rail_data["estimated_time_hours"],
                "max_amount": rail_data["max_amount"],
                "min_amount": rail_data["min_amount"],
                "success_rate": rail_data["success_rate"],
            }
        
        return {
            "region": region,
            "rails": formatted_rails,
            "corridors": corridors,
            "currencies": currencies
        }
    except Exception as e:
        log.error(f"Error getting regional rails: {str(e)}")
        return {
            "error": str(e),
            "region": region,
            "rails": {},
            "corridors": {},
            "currencies": []
        }


@router.get("/rails")
async def list_rails() -> dict:
    """List all available payment rails with characteristics."""
    return {
        "rails": [
            {"type": "SWIFT_GPI", "category": "CROSS_BORDER", "cost_level": "MEDIUM"},
            {"type": "NAMPAY", "category": "CROSS_BORDER", "cost_level": "LOW"},
            {"type": "PARTNER_NETWORK", "category": "CROSS_BORDER", "cost_level": "VERY_LOW"},
            {"type": "RTGS_BULK", "category": "DOMESTIC_BATCH", "cost_level": "VERY_LOW"},
            {"type": "BATCH_ACH", "category": "DOMESTIC_BATCH", "cost_level": "VERY_LOW"},
            {"type": "SLOW_BATCH", "category": "DOMESTIC_BATCH", "cost_level": "MINIMAL"},
        ]
    }
