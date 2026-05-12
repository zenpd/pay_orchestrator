from __future__ import annotations
import re
from agents.state import PaymentState
from shared.logger import get_logger

log = get_logger("agents.guardrails")

_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"disregard (your|all) (previous |prior )?instructions",
    r"you are now",
    r"jailbreak",
    r"system prompt",
    r"forget (your|all) (previous |prior )?instructions",
    r"act as (?:a |an )?(?:different|new|unrestricted)",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

_PII_PATTERNS = {
    "card": re.compile(r"\b(?:\d{4}[\s-]?){4}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b"),
    "account": re.compile(r"\b\d{10,20}\b"),
}


def _detect_injection(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


def _redact_pii(text: str) -> str:
    text = _PII_PATTERNS["card"].sub("[CARD_REDACTED]", text)
    text = _PII_PATTERNS["iban"].sub("[IBAN_REDACTED]", text)
    text = _PII_PATTERNS["account"].sub("[ACCT_REDACTED]", text)
    return text


def guardrails_node(state: PaymentState) -> PaymentState:
    """
    Validate and sanitise incoming payment request fields.
    Detects prompt injection in free-text fields and redacts PII.
    """
    free_text_fields = ["payment_purpose", "sender_name", "receiver_name"]
    for field in free_text_fields:
        value = state.get(field, "")
        if not isinstance(value, str):
            continue
        if _detect_injection(value):
            log.warning("injection_detected", field=field, payment_id=state.get("payment_id"))
            state["error"] = f"Prompt injection attempt detected in field '{field}'."
            return state
        state[field] = _redact_pii(value)  # type: ignore[literal-required]

    return state
