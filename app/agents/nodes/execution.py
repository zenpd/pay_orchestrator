from __future__ import annotations
import time
import random
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.execution")

# Format templates map rail → formatter function name
_FORMAT_MAP = {
    "SWIFT_GPI": "_fmt_swift_mt103",
    "SWIFT_TRADITIONAL": "_fmt_swift_mt103",
    "PayShap_INSTANT": "_fmt_iso20022",
    "PayShap_SCHEDULED": "_fmt_iso20022",
    "RTGS_HIGH_VALUE": "_fmt_rtgs",
    "RTGS_BULK": "_fmt_bankserv_acb",
    "SADC_PAY": "_fmt_iso20022",
    "CORRESPONDENT": "_fmt_correspondent",
}

# MT→MX conversion metadata
_MT_MX_MAP = {
    "SWIFT_GPI": ("MT103", "MX_pacs.008"),
    "SWIFT_TRADITIONAL": ("MT103", "MX_pacs.008"),
    "PayShap_INSTANT": ("native_MX", "native_MX"),
    "PayShap_SCHEDULED": ("native_MX", "native_MX"),
    "RTGS_HIGH_VALUE": ("RTGS_XML", "RTGS_XML"),
    "RTGS_BULK": ("BANKSERV_ACB", "BANKSERV_ACB"),
    "SADC_PAY": ("native_MX", "MX_pacs.008"),
    "CORRESPONDENT": ("PROPRIETARY", "PROPRIETARY"),
}

_RAIL_SUCCESS_RATES = {
    "SWIFT_GPI": 0.98,
    "SWIFT_TRADITIONAL": 0.96,
    "PayShap_INSTANT": 0.994,
    "PayShap_SCHEDULED": 0.991,
    "RTGS_HIGH_VALUE": 0.997,
    "RTGS_BULK": 0.989,
    "SADC_PAY": 0.970,
    "CORRESPONDENT": 0.940,
}


def execution_node(state: PaymentState) -> PaymentState:
    """
    Agent 4 — Execution.
    Formats the payment message for the selected rail and submits it,
    with automatic failover to the backup rail on failure.
    """
    log.info("execution.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    selected_rail = state.get("selected_rail", "NONE")
    backup_rail = state.get("backup_rail", "NONE")

    if selected_rail == "NONE":
        return {
            **state,
            "execution_status": "FAILED",
            "formatted_message": {},
            "rail_response": {"error": "No rail selected"},
            "execution_time": 0.0,
        }

    formatted_message = _format_message(selected_rail, state)
    conv_start = time.perf_counter()
    success, rail_response = _execute_on_rail(selected_rail)
    conversion_time_ms = (time.perf_counter() - conv_start) * 1000

    active_rail = selected_rail
    if not success and backup_rail != "NONE":
        log.warning("execution.failover", from_rail=selected_rail, to_rail=backup_rail)
        formatted_message = _format_message(backup_rail, state)
        success, rail_response = _execute_on_rail(backup_rail)
        active_rail = backup_rail if success else selected_rail

    original_fmt, converted_fmt = _MT_MX_MAP.get(active_rail, ("UNKNOWN", "UNKNOWN"))
    execution_time = time.perf_counter() - start

    log.info(
        "execution.complete",
        payment_id=state.get("payment_id"),
        rail=active_rail,
        success=success,
        elapsed_ms=round(execution_time * 1000, 1),
    )

    return {
        **state,
        "execution_status": "SUCCESS" if success else "FAILED",
        "formatted_message": formatted_message,
        "rail_response": rail_response,
        "execution_time": round(execution_time, 4),
        "original_message_format": original_fmt,
        "converted_message_format": converted_fmt,
        "conversion_time_ms": round(conversion_time_ms, 2),
    }


# ── Formatters ────────────────────────────────────────────────────────────────

def _format_message(rail: str, state: PaymentState) -> dict:
    fn_name = _FORMAT_MAP.get(rail, "_fmt_generic")
    formatters = {
        "_fmt_swift_mt103": _fmt_swift_mt103,
        "_fmt_iso20022": _fmt_iso20022,
        "_fmt_rtgs": _fmt_rtgs,
        "_fmt_bankserv_acb": _fmt_bankserv_acb,
        "_fmt_correspondent": _fmt_correspondent,
        "_fmt_generic": _fmt_generic,
    }
    return formatters[fn_name](state)


def _fmt_swift_mt103(state: PaymentState) -> dict:
    pid = state.get("payment_id", "")
    return {
        "format": "SWIFT_MT103",
        "fields": {
            "20": f"TRN{pid[-10:]}",
            "23B": "CRED",
            "32A": f"{state.get('currency_to', 'USD')}{state.get('amount', 0):.2f}",
            "50K": (state.get("sender_name", "") or "")[:35],
            "59": (state.get("receiver_name", "") or "")[:35],
            "70": (state.get("payment_purpose", "") or "")[:35],
            "71A": "SHA",
        },
        "character_set": "SWIFT_X",
    }


def _fmt_iso20022(state: PaymentState) -> dict:
    pid = state.get("payment_id", "")
    return {
        "format": "ISO20022_pacs.008",
        "fields": {
            "MsgId": f"MSG{pid[-16:]}",
            "IntrBkSttlmAmt": {
                "Ccy": state.get("currency_to", "ZAR"),
                "Value": state.get("amount", 0),
            },
            "Dbtr": {"Nm": (state.get("sender_name", "") or "")[:140]},
            "Cdtr": {"Nm": (state.get("receiver_name", "") or "")[:140]},
            "RmtInf": {"Ustrd": (state.get("payment_purpose", "") or "")[:140]},
        },
        "schema": "ISO20022_pacs.008",
    }


def _fmt_rtgs(state: PaymentState) -> dict:
    return {
        "format": "RTGS_XML",
        "fields": {
            "PaymentId": state.get("payment_id"),
            "Amount": state.get("amount", 0),
            "Currency": state.get("currency_to", "ZAR"),
            "Debtor": state.get("sender_name"),
            "Creditor": state.get("receiver_name"),
            "Purpose": state.get("payment_purpose"),
        },
        "settlement": "REAL_TIME_GROSS",
    }


def _fmt_bankserv_acb(state: PaymentState) -> dict:
    amount_cents = int((state.get("amount", 0) or 0) * 100)
    return {
        "format": "BANKSERV_ACB",
        "record": {
            "record_type": "010",
            "amount": f"{amount_cents:015d}",
            "transaction_code": "30",
            "beneficiary_name": (state.get("receiver_name", "") or "")[:32].ljust(32),
            "reference": (state.get("payment_purpose", "") or "")[:20].ljust(20),
        },
        "encoding": "ASCII",
    }


def _fmt_correspondent(state: PaymentState) -> dict:
    return {
        "format": "CORRESPONDENT_PROPRIETARY",
        "fields": {
            "reference": state.get("payment_id"),
            "amount": state.get("amount", 0),
            "currency": state.get("currency_to"),
            "sender": state.get("sender_name"),
            "receiver": state.get("receiver_name"),
            "purpose": state.get("payment_purpose"),
        },
    }


def _fmt_generic(state: PaymentState) -> dict:
    return {
        "format": "GENERIC",
        "payment_id": state.get("payment_id"),
        "amount": state.get("amount", 0),
        "currency": state.get("currency_to"),
        "sender": state.get("sender_name"),
        "receiver": state.get("receiver_name"),
    }


def _execute_on_rail(rail: str) -> tuple[bool, dict]:
    success_rate = _RAIL_SUCCESS_RATES.get(rail, 0.95)
    success = random.random() < success_rate
    if success:
        return True, {
            "status": "ACCEPTED",
            "rail": rail,
            "transaction_ref": f"TXN{random.randint(100_000, 999_999)}",
            "settlement_time": "T+0" if "INSTANT" in rail or "RTGS" in rail else "T+1",
        }
    return False, {"status": "REJECTED", "rail": rail, "error_code": "RAIL_TIMEOUT", "reason": "Rail unavailable"}
