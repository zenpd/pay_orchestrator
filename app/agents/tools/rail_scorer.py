from __future__ import annotations
from shared.scoring import score_rail
from shared.rail_constants import RAIL_PERFORMANCE


def score_all_rails(
    available_rails: list[str],
    predicted_times: dict[str, float],
    amount: float,
    risk_score: float,
    routing_preference: str = "balanced",
    urgency: int = 5,
    risk_tolerance: int = 5,
) -> dict[str, dict]:
    """Score all available rails and return a dict of rail → score breakdown."""
    scores: dict[str, dict] = {}
    for rail in available_rails:
        if rail not in RAIL_PERFORMANCE:
            continue
        scores[rail] = score_rail(
            rail_name=rail,
            performance=RAIL_PERFORMANCE[rail],
            predicted_hours=predicted_times.get(rail, 24.0),
            amount=amount,
            risk_score=risk_score,
            routing_preference=routing_preference,
            urgency=urgency,
            risk_tolerance=risk_tolerance,
        )
    return scores


def select_top_rails(scores: dict[str, dict]) -> tuple[str, str]:
    """Return (selected_rail, backup_rail) from scored dict."""
    ranked = sorted(scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
    selected = ranked[0][0] if ranked else "NONE"
    backup = ranked[1][0] if len(ranked) > 1 else "NONE"
    return selected, backup
