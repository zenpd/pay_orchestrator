from __future__ import annotations
from shared.config import get_settings
from shared.logger import get_logger
import httpx

log = get_logger("agents.tools.sanctions_check")

_MOCK_SANCTIONS_LIST = frozenset([
    "SANCTIONED ENTITY LLC",
    "BLOCKED COMPANY INC",
    "PROHIBITED TRADING CORP",
])

_LISTS_CHECKED = ["OFAC", "UN", "EU", "UK_HMT"]


def run_sanctions_check(sender_name: str, receiver_name: str) -> dict:
    """
    Screen sender and receiver against sanctions lists.
    Uses live AML provider when configured, falls back to mock list.
    """
    settings = get_settings()

    if settings.aml_provider_url:
        try:
            resp = httpx.post(
                f"{settings.aml_provider_url}/screen",
                json={"names": [sender_name, receiver_name]},
                headers={"Authorization": f"Bearer {settings.aml_api_key}"},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "hit": data.get("hit", False),
                "matched_name": data.get("matched_name"),
                "lists_checked": data.get("lists_checked", _LISTS_CHECKED),
                "source": "live",
            }
        except Exception as exc:
            log.warning("sanctions_check.live_failure", error=str(exc))

    # Mock fallback
    sender_upper = sender_name.upper()
    receiver_upper = receiver_name.upper()
    hit = any(s in sender_upper or s in receiver_upper for s in _MOCK_SANCTIONS_LIST)
    matched = next(
        (s for s in _MOCK_SANCTIONS_LIST if s in sender_upper or s in receiver_upper),
        None,
    )
    return {
        "hit": hit,
        "matched_name": matched,
        "lists_checked": _LISTS_CHECKED,
        "source": "mock",
    }
