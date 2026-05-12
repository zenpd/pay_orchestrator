from __future__ import annotations
import time
from shared.scoring import score_rail
from shared.logger import get_logger
from agents.state import PaymentState

log = get_logger("agents.nodes.optimizer")


def optimizer_node(state: PaymentState) -> PaymentState:
    """
    Agent 3 — Optimizer.
    Scores every available rail with a multi-objective function and
    selects the primary and backup rail.
    """
    log.info("optimizer.start", payment_id=state.get("payment_id"))
    start = time.perf_counter()

    available_rails = state.get("corridor_metadata", {}).get("available_rails", [])
    rail_performance = state.get("rail_performance", {})
    predicted_times = state.get("predicted_processing_times", {})
    amount = state.get("amount", 0.0)
    risk_score = state.get("risk_score", 0.0)
    routing_preference = state.get("routing_preference", "balanced")
    urgency = state.get("urgency", 5)
    risk_tolerance = state.get("risk_tolerance", 5)

    if not available_rails:
        log.warning("optimizer.no_rails", payment_id=state.get("payment_id"))
        return {
            **state,
            "selected_rail": "NONE",
            "backup_rail": "NONE",
            "routing_score": {},
            "optimization_reasoning": "No available rails for this corridor.",
        }

    rail_scores: dict = {}
    for rail in available_rails:
        if rail not in rail_performance:
            continue
        rail_scores[rail] = score_rail(
            rail_name=rail,
            performance=rail_performance[rail],
            predicted_hours=predicted_times.get(rail, 24.0),
            amount=amount,
            risk_score=risk_score,
            routing_preference=routing_preference,
            urgency=urgency,
            risk_tolerance=risk_tolerance,
        )

    if not rail_scores:
        return {
            **state,
            "selected_rail": "NONE",
            "backup_rail": "NONE",
            "routing_score": {},
            "optimization_reasoning": "No scoreable rails found.",
        }

    sorted_rails = sorted(rail_scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
    selected_rail, selected_score = sorted_rails[0]
    backup_rail = sorted_rails[1][0] if len(sorted_rails) > 1 else "NONE"

    reasoning = _build_reasoning(selected_rail, selected_score, amount, routing_preference)

    elapsed_ms = (time.perf_counter() - start) * 1000
    log.info(
        "optimizer.complete",
        payment_id=state.get("payment_id"),
        selected_rail=selected_rail,
        score=round(selected_score["total_score"], 4),
        backup_rail=backup_rail,
        elapsed_ms=round(elapsed_ms, 1),
    )

    return {
        **state,
        "selected_rail": selected_rail,
        "backup_rail": backup_rail,
        "routing_score": rail_scores,
        "optimization_reasoning": reasoning,
    }


def _build_reasoning(rail: str, score: dict, amount: float, preference: str) -> str:
    parts: list[str] = [f"Selected {rail} for {preference} routing (score={score['total_score']:.3f})"]
    if score["cost_score"] > 0.80:
        parts.append(f"low cost (${score['breakdown']['cost_usd']:.2f})")
    if score["speed_score"] > 0.80:
        parts.append(f"fast ({score['breakdown']['processing_hours']:.2f}h)")
    if score["success_score"] > 0.95:
        parts.append(f"high reliability ({score['breakdown']['success_rate']*100:.1f}%)")
    if amount > 100_000:
        parts.append("high-value transaction — enhanced tracking required")
    return "; ".join(parts)
