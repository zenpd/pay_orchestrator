from __future__ import annotations
import re
from shared.logger import get_logger

log = get_logger("security.guardrails")

_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore previous instructions",
        r"you are now",
        r"jailbreak",
        r"system prompt",
        r"forget (your|all) (previous |prior )?instructions",
        r"act as (?:a |an )?(?:different|new|unrestricted)",
    ]
]


def is_injection(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def validate_payment_input(data: dict) -> list[str]:
    """Return a list of security violations found in payment input data."""
    violations: list[str] = []
    for field in ("payment_purpose", "sender_name", "receiver_name"):
        value = data.get(field, "")
        if isinstance(value, str) and is_injection(value):
            violations.append(f"INJECTION_DETECTED:{field}")
            log.warning("security.injection_attempt", field=field)
    return violations
