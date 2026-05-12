from __future__ import annotations
from fastapi import APIRouter, Depends
from api.auth import get_current_user
from api.schemas.output import SessionMetricsResponse

router = APIRouter()

# In-memory counters — replaced by Redis/Postgres in production
_metrics: dict = {
    "total_payments": 0,
    "successful_payments": 0,
    "failed_payments": 0,
    "compliance_approvals": 0,
    "compliance_rejections": 0,
    "compliance_holds": 0,
    "rails_used": {},
    "preference_counts": {},
}


@router.get("/session", response_model=SessionMetricsResponse)
async def get_session_metrics(user: dict = Depends(get_current_user)) -> SessionMetricsResponse:
    total = _metrics["total_payments"]
    success_rate = (
        round(_metrics["successful_payments"] / total * 100, 1) if total else 0.0
    )
    return SessionMetricsResponse(
        total_payments=total,
        successful_payments=_metrics["successful_payments"],
        failed_payments=_metrics["failed_payments"],
        success_rate_pct=success_rate,
        compliance_approvals=_metrics["compliance_approvals"],
        compliance_rejections=_metrics["compliance_rejections"],
        compliance_holds=_metrics["compliance_holds"],
        rails_used=_metrics["rails_used"],
        preference_counts=_metrics["preference_counts"],
    )


@router.post("/reset", status_code=204)
async def reset_metrics(user: dict = Depends(get_current_user)) -> None:
    global _metrics
    _metrics = {
        "total_payments": 0,
        "successful_payments": 0,
        "failed_payments": 0,
        "compliance_approvals": 0,
        "compliance_rejections": 0,
        "compliance_holds": 0,
        "rails_used": {},
        "preference_counts": {},
    }
