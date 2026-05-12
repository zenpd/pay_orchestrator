from __future__ import annotations
from fastapi import APIRouter, Query
from shared.rail_constants import CORRIDORS

router = APIRouter()


@router.get("")
async def list_corridors(
    sender_country: str | None = Query(None, description="ISO-3166 2-letter sender country code"),
    receiver_country: str | None = Query(None, description="ISO-3166 2-letter receiver country code"),
) -> dict:
    if sender_country and receiver_country:
        key = f"{sender_country.upper()}_{receiver_country.upper()}"
        corridor = CORRIDORS.get(key)
        if corridor:
            return {key: corridor}
        return {}

    if sender_country:
        prefix = sender_country.upper()
        return {k: v for k, v in CORRIDORS.items() if k.startswith(prefix)}

    return CORRIDORS
