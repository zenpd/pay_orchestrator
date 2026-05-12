from __future__ import annotations
import time
from typing import Any
from shared.rail_constants import HIGH_RISK_COUNTRIES, RISK_SCORE_REJECT, RISK_SCORE_HOLD
from shared.scoring import classify_compliance
from shared.logger import get_logger
from agents.state import PaymentState
from agents.tools.sanctions_check import run_sanctions_check

log = get_logger("agents.nodes.policy_reasoner")

_SANCTIONS_LIST = frozenset([
    "SANCTIONED ENTITY LLC",
    "BLOCKED COMPANY INC",
    "PROHIBITED TRADING CORP",
])

_COUNTRY_RULES: dict[str, dict[str, Any]] = {
    "US": {"max_transaction_limit": 100_000, "requires_purpose_code": True, "requires_tax_id": True},
    "GB": {"max_transaction_limit": 150_000, "requires_purpose_code": False, "requires_tax_id": False},
    "ZA": {"max_transaction_limit": 1_000_000, "requires_purpose_code": True, "requires_tax_id": True},
}

_SUSPICIOUS_KEYWORDS = frozenset(["cash", "diamonds", "gold bullion", "bearer bonds", "shell company"])
_LEGITIMATE_KEYWORDS = frozenset(["trade", "invoice", "salary", "goods", "services", "settlement", "investment"])


def policy_reasoner_node(state: PaymentState) -> PaymentState:
    """
    Agent 2 — Policy Reasoner.
    Runs left-shifted compliance validation:
      1. AML / sanctions screening
      2. High-risk country check
      3. Country-specific rules
      4. Transaction limits
      5. Payment purpose analysis
    """
    log.info("policy_reasoner.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    violations: list[str] = []
    warnings: list[str] = []
    risk_factors: list[str] = []
    compliance_checks: list[tuple[str, bool]] = []

    sender = state.get("sender_name", "")
    receiver = state.get("receiver_name", "")
    amount = state.get("amount", 0.0)
    sender_country = state.get("sender_country", "")
    receiver_country = state.get("receiver_country", "")
    purpose = state.get("payment_purpose", "")

    # 1. AML / Sanctions screening
    sanctions_result = run_sanctions_check(sender, receiver)
    aml_cleared = not sanctions_result.get("hit", False)
    sanctions_check_status = "CLEARED" if aml_cleared else "BLOCKED"
    compliance_checks.append(("AML Screening", aml_cleared))
    if not aml_cleared:
        risk_factors.append("AML_ALERT")
        violations.append("SANCTIONS_HIT")

    # 2. High-risk country check
    high_risk = (
        sender_country in HIGH_RISK_COUNTRIES
        or receiver_country in HIGH_RISK_COUNTRIES
    )
    compliance_checks.append(("High-Risk Countries", not high_risk))
    if high_risk:
        risk_factors.append("HIGH_RISK_COUNTRY")
        violations.append(f"HIGH_RISK_COUNTRY:{receiver_country}")

    # 3. Country-specific rules
    country_rules = _COUNTRY_RULES.get(receiver_country, {})
    if country_rules:
        if amount > country_rules.get("max_transaction_limit", float("inf")):
            violations.append(f"EXCEEDS_{receiver_country}_LIMIT")
        if country_rules.get("requires_purpose_code") and not purpose:
            violations.append("MISSING_PURPOSE_CODE")
        if country_rules.get("requires_tax_id"):
            warnings.append("TAX_ID_VALIDATION_REQUIRED")
    compliance_checks.append(("Country Rules", not any(v.startswith(f"EXCEEDS_{receiver_country}") for v in violations)))

    # 4. Transaction limits
    global_limit_ok = amount <= 500_000
    corridor_metadata = state.get("corridor_metadata", {})
    if corridor_metadata.get("compliance_level") == "HIGH" and amount > 250_000:
        global_limit_ok = False
    compliance_checks.append(("Transaction Limits", global_limit_ok))
    if not global_limit_ok:
        risk_factors.append("LIMIT_EXCEEDED")
        violations.append("AMOUNT_EXCEEDS_CORRIDOR_LIMIT")

    # 5. Purpose analysis
    purpose_lower = purpose.lower()
    has_suspicious = any(kw in purpose_lower for kw in _SUSPICIOUS_KEYWORDS)
    has_legitimate = any(kw in purpose_lower for kw in _LEGITIMATE_KEYWORDS)
    purpose_ok = has_legitimate or not has_suspicious
    compliance_checks.append(("Purpose Analysis", purpose_ok))
    if not purpose_ok:
        risk_factors.append("SUSPICIOUS_PURPOSE")
        violations.append("SUSPICIOUS_PURPOSE_DETECTED")

    # ML fraud score (mock)
    import random
    fraud_check_score = round(random.uniform(0.01, 0.30), 3)

    # Risk score calculation
    failed = sum(1 for _, passed in compliance_checks if not passed)
    total = len(compliance_checks)
    base_score = failed / total if total else 0
    critical_count = sum(1 for f in risk_factors if f in ("AML_ALERT", "HIGH_RISK_COUNTRY", "SUSPICIOUS_PURPOSE"))
    risk_score = min(1.0, base_score + critical_count * 0.20)

    compliance_status = classify_compliance(risk_score)
    if compliance_status == "APPROVED":
        compliance_notes = "All compliance checks passed."
    elif compliance_status == "HOLD_FOR_REVIEW":
        compliance_notes = f"Manual review required: {', '.join(risk_factors)}"
    else:
        compliance_notes = f"Payment rejected — high risk: {', '.join(risk_factors)}"

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info(
        "policy_reasoner.complete",
        payment_id=state.get("payment_id"),
        status=compliance_status,
        risk_score=risk_score,
        elapsed_ms=round(elapsed_ms, 1),
    )

    return {
        **state,
        "compliance_status": compliance_status,
        "risk_score": risk_score,
        "aml_cleared": aml_cleared,
        "sanctions_cleared": aml_cleared,
        "compliance_notes": compliance_notes,
        "validation_violations": violations,
        "validation_warnings": warnings,
        "fraud_check_score": fraud_check_score,
        "sanctions_check_status": sanctions_check_status,
    }
