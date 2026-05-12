from __future__ import annotations
import time
from shared.helpers import build_corridor_key
from shared.rail_constants import CORRIDORS, FX_RATES, RAIL_PERFORMANCE, PRE_VALIDATION_RULES
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.context_collector")


def context_collector_node(state: PaymentState) -> PaymentState:
    """
    Agent 1 — Context Collector.
    Enriches the payment state with FX rate, corridor metadata,
    rail performance, predicted processing times, and pre-validation rules.
    """
    log.info("context_collector.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    corridor_key = build_corridor_key(
        state.get("sender_country", ""),
        state.get("receiver_country", ""),
    )

    # ── FX rate ──────────────────────────────────────────────────────────────
    currency_pair = f"{state.get('currency_from', 'ZAR')}_{state.get('currency_to', 'USD')}"
    base_rate = FX_RATES.get(currency_pair, FX_RATES.get(f"{state.get('currency_to', 'USD')}_{state.get('currency_from', 'ZAR')}", 1.0))
    spread = 0.002  # 0.2% bank spread
    fx_rate_details = {
        "pair": currency_pair,
        "mid_rate": base_rate,
        "bid": round(base_rate * (1 - spread), 6),
        "ask": round(base_rate * (1 + spread), 6),
        "source": "mock_fx_feed",
        "timestamp": time.time(),
    }

    # ── Corridor metadata ─────────────────────────────────────────────────────
    corridor_metadata = CORRIDORS.get(corridor_key, {
        "available_rails": ["SWIFT_GPI", "CORRESPONDENT"],
        "default_rail": "SWIFT_GPI",
        "compliance_level": "HIGH",
        "regulatory_requirements": ["FICA"],
        "eft_replacement": None,
    })

    # ── Rail performance ──────────────────────────────────────────────────────
    available_rails = corridor_metadata.get("available_rails", [])
    rail_performance = {r: RAIL_PERFORMANCE[r] for r in available_rails if r in RAIL_PERFORMANCE}

    # ── Predicted processing times ────────────────────────────────────────────
    amount = state.get("amount", 0.0)
    predicted_processing_times: dict[str, float] = {}
    for rail, perf in rail_performance.items():
        base_hours = perf["avg_processing_hours"]
        # Amount factor: +20% for large payments, -10% for micro payments
        if amount > 100_000:
            base_hours *= 1.20
        elif amount < 10_000:
            base_hours *= 0.90
        # Popular corridor discount
        if corridor_metadata.get("compliance_level") == "LOW":
            base_hours *= 0.85
        predicted_processing_times[rail] = round(base_hours, 4)

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info(
        "context_collector.complete",
        payment_id=state.get("payment_id"),
        corridor=corridor_key,
        rails=list(rail_performance.keys()),
        elapsed_ms=round(elapsed_ms, 1),
    )

    return {
        **state,
        "fx_rate": base_rate,
        "fx_rate_details": fx_rate_details,
        "corridor_metadata": corridor_metadata,
        "rail_performance": rail_performance,
        "predicted_processing_times": predicted_processing_times,
        "validation_rules": PRE_VALIDATION_RULES,
    }
