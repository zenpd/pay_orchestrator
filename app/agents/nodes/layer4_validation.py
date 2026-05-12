from __future__ import annotations
import time
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.layer4_validation")

_BACKOFFICE_SYSTEMS = ["T24", "Finacle", "SAP", "EE"]
_PAYMENT_SYSTEMS = {"SWIFT_GPI": "PayEx", "SWIFT_TRADITIONAL": "PayEx", "RTGS_HIGH_VALUE": "BOLPES"}
_DEFAULT_PAYMENT_SYSTEM = "ICM"

_MOCK_AVAILABLE_BALANCE = 500_000.0


def layer4_validation_node(state: PaymentState) -> PaymentState:
    """
    Layer 4 validation — checks back-office systems and payment processing
    platform readiness before execution.
    """
    log.info("layer4_validation.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    amount = state.get("amount", 0.0)
    selected_rail = state.get("selected_rail", "")

    # ── Back-office validation ─────────────────────────────────────────────
    balance_ok = _MOCK_AVAILABLE_BALANCE >= amount
    balance_check = {
        "available_balance": _MOCK_AVAILABLE_BALANCE,
        "required": amount,
        "sufficient": balance_ok,
        "validated_by": _BACKOFFICE_SYSTEMS,
    }

    account_status = {
        "status": "ACTIVE",
        "gl_balance_ok": True,
        "fx_limit_ok": True,
        "validated_by": ["T24", "Finacle"],
    }

    # ── Payment processing system ──────────────────────────────────────────
    processing_system = _PAYMENT_SYSTEMS.get(selected_rail, _DEFAULT_PAYMENT_SYSTEM)
    rail_ready = selected_rail in {
        "SWIFT_GPI", "SWIFT_TRADITIONAL", "PayShap_INSTANT", "PayShap_SCHEDULED",
        "RTGS_HIGH_VALUE", "RTGS_BULK", "SADC_PAY", "CORRESPONDENT",
    }
    processing_check = {
        "system": processing_system,
        "rail_ready": rail_ready,
        "rail": selected_rail,
    }

    validation_ok = balance_ok and account_status["status"] == "ACTIVE" and rail_ready
    validation_status = "APPROVED" if validation_ok else "REJECTED"

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info(
        "layer4_validation.complete",
        payment_id=state.get("payment_id"),
        status=validation_status,
        elapsed_ms=round(elapsed_ms, 1),
    )

    return {
        **state,
        "layer4_balance_check": balance_check,
        "layer4_account_status": account_status,
        "layer4_validation_status": validation_status,
        "layer4_validation_details": {"backoffice": balance_check, "processing": processing_check},
    }
