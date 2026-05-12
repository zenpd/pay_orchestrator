from __future__ import annotations
from shared.rail_constants import HIGH_RISK_COUNTRIES, CORRIDORS
from shared.logger import get_logger

log = get_logger("security.compliance")


def check_corridor_compliance(sender_country: str, receiver_country: str) -> dict:
    """
    Verify that the corridor exists and flag regulatory requirements.
    """
    corridor_key = f"{sender_country.upper()}_{receiver_country.upper()}"
    corridor = CORRIDORS.get(corridor_key)

    issues: list[str] = []
    if sender_country.upper() in HIGH_RISK_COUNTRIES:
        issues.append(f"SENDER_HIGH_RISK_COUNTRY:{sender_country}")
    if receiver_country.upper() in HIGH_RISK_COUNTRIES:
        issues.append(f"RECEIVER_HIGH_RISK_COUNTRY:{receiver_country}")

    return {
        "corridor_key": corridor_key,
        "corridor_supported": corridor is not None,
        "compliance_level": corridor.get("compliance_level", "UNKNOWN") if corridor else "UNKNOWN",
        "regulatory_requirements": corridor.get("regulatory_requirements", []) if corridor else [],
        "issues": issues,
    }
