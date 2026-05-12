from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_current_user
from api.schemas.input import ProcessPaymentRequest
from api.schemas.output import PaymentResponse, PaymentStatusResponse
from agents.graph import compiled_graph
from agents.state import PaymentState
from shared.helpers import generate_id
from shared.logger import get_logger

log = get_logger("api.routers.payments")
router = APIRouter()


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    req: ProcessPaymentRequest,
    user: dict = Depends(get_current_user),
) -> PaymentResponse:
    payment_id = generate_id("PAY")
    session_id = str(uuid.uuid4())[:8]
    state_key = f"{payment_id}:{session_id}"

    initial_state: PaymentState = {
        "state_key": state_key,
        "payment_id": payment_id,
        "amount": req.amount,
        "currency_from": req.currency_from,
        "currency_to": req.currency_to,
        "sender_country": req.sender_country,
        "receiver_country": req.receiver_country,
        "payment_purpose": req.payment_purpose,
        "sender_name": req.sender_name,
        "receiver_name": req.receiver_name,
        "routing_preference": req.routing_preference,
        "urgency": req.urgency,
        "risk_tolerance": req.risk_tolerance,
        "messages": [],
    }

    try:
        result: PaymentState = compiled_graph.invoke(initial_state)
    except Exception as exc:
        log.error("payments.process_error", payment_id=payment_id, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Orchestration error: {exc}")

    return _build_response(result)


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    user: dict = Depends(get_current_user),
) -> PaymentStatusResponse:
    # In production this would be fetched from the DB / Redis cache.
    raise HTTPException(status_code=404, detail="Payment not found in this session.")


def _build_response(state: PaymentState) -> PaymentResponse:
    selected_rail = state.get("selected_rail", "NONE")
    orig_fmt = state.get("original_message_format", "")
    conv_fmt = state.get("converted_message_format", "")

    message_conversion = None
    if orig_fmt and orig_fmt != conv_fmt:
        message_conversion = {
            "original_format": orig_fmt,
            "converted_format": conv_fmt,
            "conversion_time_ms": state.get("conversion_time_ms"),
            "eft_replacement_ready": True,
        }

    return PaymentResponse(
        payment_id=state.get("payment_id", ""),
        state_key=state.get("state_key", ""),
        compliance_status=state.get("compliance_status", "UNKNOWN"),
        risk_score=state.get("risk_score", 0.0),
        selected_rail=selected_rail,
        backup_rail=state.get("backup_rail", "NONE"),
        execution_status=state.get("execution_status", "NOT_EXECUTED"),
        optimization_reasoning=state.get("optimization_reasoning"),
        validation_violations=state.get("validation_violations", []),
        validation_warnings=state.get("validation_warnings", []),
        fraud_check_score=state.get("fraud_check_score"),
        sanctions_check_status=state.get("sanctions_check_status"),
        actual_cost=state.get("actual_cost"),
        actual_processing_time=state.get("actual_processing_time"),
        message_conversion=message_conversion,
        selection_details=state.get("routing_score"),
        error=state.get("error"),
    )
