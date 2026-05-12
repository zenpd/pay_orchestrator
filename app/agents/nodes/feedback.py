from __future__ import annotations
import time
import random
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.feedback")

_TRAINING_EXAMPLES: list[dict] = []
_RETRAINING_TRIGGER_COUNT = 100
_RETRAINING_ACCURACY_THRESHOLD = 0.70


def feedback_node(state: PaymentState) -> PaymentState:
    """
    Agent 5 — Feedback.
    Calculates actual vs predicted cost/time, computes performance delta,
    and stores a training example for model retraining.
    """
    log.info("feedback.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    predicted_times = state.get("predicted_processing_times", {})
    selected_rail = state.get("selected_rail", "")
    predicted_time = predicted_times.get(selected_rail, 24.0)

    success = state.get("execution_status") == "SUCCESS"

    # ── Actual cost (± 10% variance from rail avg) ─────────────────────────
    routing_score = state.get("routing_score", {})
    base_cost = routing_score.get(selected_rail, {}).get("breakdown", {}).get("cost_usd", 15.0)
    cost_variance = random.uniform(-0.10, 0.10)
    actual_cost = round(base_cost * (1 + cost_variance), 2)
    if state.get("amount", 0) > 100_000:
        actual_cost += 10.0  # surcharge for high-value

    # ── Actual processing time ─────────────────────────────────────────────
    time_variance = random.uniform(-0.10, 0.10)
    actual_time = predicted_time * (1 + time_variance)
    if not success:
        actual_time *= 1.5  # failed payments take longer to resolve
    actual_time = round(actual_time, 4)

    # ── Performance delta ──────────────────────────────────────────────────
    pred_cost = routing_score.get(selected_rail, {}).get("breakdown", {}).get("cost_usd", base_cost)
    performance_delta = {
        "cost_delta_usd": round(actual_cost - pred_cost, 2),
        "time_delta_hours": round(actual_time - predicted_time, 4),
        "cost_accuracy_pct": round(100 - abs(actual_cost - pred_cost) / max(pred_cost, 0.01) * 100, 1),
        "time_accuracy_pct": round(100 - abs(actual_time - predicted_time) / max(predicted_time, 0.001) * 100, 1),
        "success": success,
    }

    # ── Store training example ─────────────────────────────────────────────
    training_example = {
        "payment_id": state.get("payment_id"),
        "selected_rail": selected_rail,
        "routing_preference": state.get("routing_preference"),
        "amount": state.get("amount"),
        "risk_score": state.get("risk_score"),
        "actual_cost": actual_cost,
        "actual_time": actual_time,
        "success": success,
        "performance_delta": performance_delta,
    }
    _TRAINING_EXAMPLES.append(training_example)

    if len(_TRAINING_EXAMPLES) >= _RETRAINING_TRIGGER_COUNT:
        avg_accuracy = sum(
            (e["performance_delta"]["cost_accuracy_pct"] + e["performance_delta"]["time_accuracy_pct"]) / 2
            for e in _TRAINING_EXAMPLES[-_RETRAINING_TRIGGER_COUNT:]
        ) / _RETRAINING_TRIGGER_COUNT
        if avg_accuracy < _RETRAINING_ACCURACY_THRESHOLD * 100:
            log.warning("feedback.retraining_trigger", avg_accuracy=round(avg_accuracy, 1))

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info(
        "feedback.complete",
        payment_id=state.get("payment_id"),
        success=success,
        actual_cost=actual_cost,
        elapsed_ms=round(elapsed_ms, 1),
    )

    return {
        **state,
        "actual_cost": actual_cost,
        "actual_processing_time": actual_time,
        "success": success,
        "feedback_notes": "Metrics recorded." if success else "Payment failed — metrics flagged for review.",
        "performance_delta": performance_delta,
    }
