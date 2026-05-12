from __future__ import annotations
from fastapi import APIRouter
from shared.rail_constants import RAIL_PERFORMANCE, CORRIDORS
from agents.tools.fx_rates import get_fx_rate

router = APIRouter()


@router.get("")
async def list_rails() -> dict:
    return {"rails": RAIL_PERFORMANCE, "corridors": {k: v["available_rails"] for k, v in CORRIDORS.items()}}


@router.get("/fx-rate")
async def fx_rate(
    currency_from: str = "ZAR",
    currency_to: str = "USD",
) -> dict:
    return get_fx_rate(currency_from, currency_to)
