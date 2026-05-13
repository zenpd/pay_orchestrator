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

        # Invoke workflow
        final_state = payment_orchestration_graph.invoke(state)

        # Format response
        rail_scores_response = {
            rail_type.value: RailScoreSchema(**score.__dict__)
            for rail_type, score in final_state.rail_scores.items()
        }

        return PaymentResponseSchema(
            session_id=session_id,
            stage=final_state.stage,
            selected_rail=final_state.selected_rail.value if final_state.selected_rail else None,
            rail_scores=rail_scores_response,
            execution_result=final_state.execution_result,
            messages=final_state.messages,
            errors=final_state.errors,
            created_at=datetime.fromisoformat(final_state.created_at) if final_state.created_at else None,
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
