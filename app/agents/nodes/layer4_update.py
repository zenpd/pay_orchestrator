from __future__ import annotations
import time
import random
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.layer4_update")


def layer4_update_node(state: PaymentState) -> PaymentState:
    """
    Layer 4 update — posts confirmed transaction to back-office and
    payment processing systems after successful execution.
    """
    log.info("layer4_update.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    pid = state.get("payment_id", "")
    amount = state.get("amount", 0.0)
    currency_from = state.get("currency_from", "ZAR")
    currency_to = state.get("currency_to", "USD")

    # ── Back-office updates ────────────────────────────────────────────────
    backoffice = {
        "T24": {
            "status": "POSTED",
            "transaction_id": f"T24-{pid[-8:]}",
            "posted_at": time.time(),
        },
        "Finacle": {
            "history_updated": True,
            "reference": f"FIN-{pid[-8:]}",
        },
        "SAP": {
            "gl_document_number": f"SAP-{random.randint(1_000_000, 9_999_999)}",
            "posting_date": time.strftime("%Y-%m-%d"),
        },
    }

    # FX position update when cross-currency
    if currency_from != currency_to:
        backoffice["EE"] = {
            "fx_position_updated": True,
            "pair": f"{currency_from}/{currency_to}",
            "fx_rate": state.get("fx_rate", 1.0),
        }

    # ── Payment processing update ──────────────────────────────────────────
    payment_processing = {
        "system": "ICM",
        "status": "CONFIRMED",
        "settlement_ref": f"SET-{pid[-8:]}",
        "confirmed_at": time.time(),
    }

    # ── Reconciliation data ────────────────────────────────────────────────
    reconciliation = {
        "payment_id": pid,
        "amount": amount,
        "currency_from": currency_from,
        "currency_to": currency_to,
        "fx_rate": state.get("fx_rate", 1.0),
        "selected_rail": state.get("selected_rail"),
        "execution_status": state.get("execution_status"),
        "reconciled_at": time.time(),
    }

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info("layer4_update.complete", payment_id=pid, elapsed_ms=round(elapsed_ms, 1))

    return {
        **state,
        "layer4_confirmation": {"backoffice": backoffice, "payment_processing": payment_processing},
        "layer4_reconciliation": reconciliation,
    }
