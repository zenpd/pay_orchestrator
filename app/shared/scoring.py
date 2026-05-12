from __future__ import annotations
from typing import Any
from shared.rail_constants import RISK_SCORE_REJECT, RISK_SCORE_HOLD


def score_rail(
    rail_name: str,
    performance: dict,
    predicted_hours: float,
    amount: float,
    risk_score: float,
    routing_preference: str = "balanced",
    urgency: int = 5,
    risk_tolerance: int = 5,
) -> dict[str, Any]:
    """
    Multi-objective rail scorer.

    Returns a dict with ``total_score`` and component scores.
    """
    # Preference weights
    if routing_preference == "fastest":
        speed_weight, cost_weight = 0.80, 0.20
    elif routing_preference == "cheapest":
        speed_weight, cost_weight = 0.20, 0.80
    else:  # balanced
        speed_weight, cost_weight = 0.50, 0.50

    # Normalise cost: $0.15–$35 range → 0–1 (lower cost = higher score)
    cost = performance.get("avg_cost_usd", 20)
    cost_score = max(0.0, min(1.0, 1 - (cost - 0.15) / 34.85))

    # Normalise speed: 0.017–48 hours → 0–1 (lower time = higher score)
    speed_score = max(0.0, min(1.0, 1 - (predicted_hours - 0.017) / 47.983))

    # Success probability
    success_score = (performance.get("success_rate", 0.95) + performance.get("availability", 0.99)) / 2

    # Compliance/risk (inverse)
    compliance_score = 1 - risk_score

    base_score = speed_score * speed_weight + cost_score * cost_weight

    # Risk penalty
    risk_penalties = {"VERY_LOW": 0.0, "LOW": 0.05, "MEDIUM": 0.15, "HIGH": 0.30}
    risk_penalty = risk_penalties.get(performance.get("risk_level", "MEDIUM"), 0.15)
    risk_penalty *= max(0, 1 - risk_tolerance / 15)

    # Regulatory overhead penalty
    reg_penalties = {"LOW": 0.0, "MEDIUM": 0.05, "HIGH": 0.10}
    reg_penalty = reg_penalties.get(performance.get("regulatory_overhead", "MEDIUM"), 0.05)

    # High-value bonus for SWIFT_GPI
    if amount > 100_000 and rail_name == "SWIFT_GPI":
        success_score = min(1.0, success_score * 1.05)

    # High load penalty
    if performance.get("current_load") == "HIGH":
        speed_score *= 0.7
        success_score *= 0.9

    total_score = max(0.0, base_score + success_score * 0.15 + compliance_score * 0.10 - risk_penalty - reg_penalty)

    return {
        "total_score": total_score,
        "cost_score": cost_score,
        "speed_score": speed_score,
        "success_score": success_score,
        "compliance_score": compliance_score,
        "breakdown": {
            "cost_usd": cost,
            "processing_hours": predicted_hours,
            "success_rate": performance.get("success_rate", 0.95),
            "availability": performance.get("availability", 0.99),
        },
    }


def classify_compliance(risk_score: float) -> str:
    if risk_score >= RISK_SCORE_REJECT:
        return "REJECTED"
    if risk_score >= RISK_SCORE_HOLD:
        return "HOLD_FOR_REVIEW"
    return "APPROVED"
