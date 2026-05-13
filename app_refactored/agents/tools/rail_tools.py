"""Tool definitions for payment rail analysis."""
from __future__ import annotations

import json
from typing import Any, Optional


def get_rail_data(rail_type: str) -> dict:
    """Fetch rail characteristics and performance metrics."""
    # Mock implementation — in production, fetch from database
    rails = {
        "SWIFT_GPI": {
            "type": "CROSS_BORDER",
            "success_rate": 0.98,
            "avg_cost_usd": 12.50,
            "speed_score": 75,
            "cost_score": 40,
            "max_amount": 10000000,
            "risk_level": "MEDIUM",
        },
        "NAMPAY": {
            "type": "CROSS_BORDER",
            "success_rate": 0.95,
            "avg_cost_usd": 8.00,
            "speed_score": 85,
            "cost_score": 70,
            "max_amount": 500000,
            "risk_level": "LOW",
        },
        "PARTNER_NETWORK": {
            "type": "CROSS_BORDER",
            "success_rate": 0.92,
            "avg_cost_usd": 6.00,
            "speed_score": 65,
            "cost_score": 85,
            "max_amount": 200000,
            "risk_level": "HIGH",
        },
        "RTGS_BULK": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.99,
            "avg_cost_usd": 0.50,
            "speed_score": 30,
            "cost_score": 95,
            "max_amount": 10000000,
            "risk_level": "LOW",
        },
        "BATCH_ACH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.96,
            "avg_cost_usd": 0.20,
            "speed_score": 40,
            "cost_score": 98,
            "max_amount": 500000,
            "risk_level": "LOW",
        },
        "SLOW_BATCH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.94,
            "avg_cost_usd": 0.10,
            "speed_score": 20,
            "cost_score": 100,
            "max_amount": 100000,
            "risk_level": "LOW",
        },
    }
    return rails.get(rail_type, {})


def check_rail_eligibility(
    rail_type: str, amount: float, corridor: str
) -> dict:
    """Check if a rail is eligible for this payment."""
    rail_data = get_rail_data(rail_type)
    if not rail_data:
        return {"eligible": False, "reason": "Unknown rail type"}

    max_amount = rail_data.get("max_amount", 0)
    if amount > max_amount:
        return {
            "eligible": False,
            "reason": f"Amount {amount} exceeds max {max_amount}",
        }

    return {"eligible": True}


def estimate_cost(rail_type: str, amount: float) -> float:
    """Estimate processing cost for a given rail."""
    rail_data = get_rail_data(rail_type)
    if not rail_data:
        return 0.0

    base_cost = rail_data.get("avg_cost_usd", 0.0)
    # Mock percentage-based costs for larger amounts
    if amount > 100000:
        percentage = 0.001  # 0.1% for large transfers
        return max(base_cost, amount * percentage)
    return base_cost


def estimate_processing_time(rail_type: str, corridor: str) -> str:
    """Estimate processing time for a given rail."""
    rail_data = get_rail_data(rail_type)
    if not rail_data:
        return "UNKNOWN"

    speed_score = rail_data.get("speed_score", 0)
    if speed_score >= 70:
        return "FAST (< 1 hour)"
    elif speed_score >= 40:
        return "MEDIUM (1-4 hours)"
    else:
        return "SLOW (> 4 hours)"
