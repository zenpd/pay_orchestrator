from __future__ import annotations
import uuid
import re
from datetime import date, datetime


def generate_id(prefix: str = "PAY") -> str:
    """Return a short prefixed UUID segment."""
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def parse_currency(value: str | float | int) -> float:
    """Coerce a currency string or number to float."""
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d.]", "", str(value))
    return float(cleaned) if cleaned else 0.0


def format_amount(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def normalize_country_code(code: str) -> str:
    """Uppercase and trim a 2-letter ISO country code."""
    return code.strip().upper()[:2]


def build_corridor_key(sender_country: str, receiver_country: str) -> str:
    return f"{normalize_country_code(sender_country)}_{normalize_country_code(receiver_country)}"


def redact_pii(text: str) -> str:
    """Redact account numbers and card-like sequences from text."""
    text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD_REDACTED]", text)
    text = re.sub(r"\b\d{10,20}\b", "[ACCT_REDACTED]", text)
    return text
