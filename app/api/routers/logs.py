from __future__ import annotations
from collections import deque
from fastapi import APIRouter, Query
from shared.logger import get_logger

router = APIRouter()
log = get_logger("api.routers.logs")

_log_buffer: deque[dict] = deque(maxlen=1000)


@router.get("")
async def get_logs(last_n: int = Query(100, ge=1, le=1000)) -> dict:
    entries = list(_log_buffer)[-last_n:]
    return {"count": len(entries), "logs": entries}


@router.post("/clear", status_code=204)
async def clear_logs() -> None:
    _log_buffer.clear()
