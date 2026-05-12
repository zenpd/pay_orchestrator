from __future__ import annotations
from shared.rail_constants import FX_RATES
from shared.config import get_settings
from shared.logger import get_logger
import httpx

log = get_logger("agents.tools.fx_rates")


def get_fx_rate(currency_from: str, currency_to: str) -> dict:
    """
    Return FX rate details for a currency pair.
    Uses live provider when configured, falls back to mock rates.
    """
    settings = get_settings()
    pair = f"{currency_from.upper()}_{currency_to.upper()}"

    if settings.fx_provider_url:
        try:
            resp = httpx.get(
                f"{settings.fx_provider_url}/rates",
                params={"from": currency_from, "to": currency_to},
                headers={"Authorization": f"Bearer {settings.fx_api_key}"},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            mid_rate = float(data["rate"])
            spread = 0.002
            return {
                "pair": pair,
                "mid_rate": mid_rate,
                "bid": round(mid_rate * (1 - spread), 6),
                "ask": round(mid_rate * (1 + spread), 6),
                "source": "live",
            }
        except Exception as exc:
            log.warning("fx_rates.live_failure", pair=pair, error=str(exc))

    # Mock fallback
    mid_rate = FX_RATES.get(pair, 1.0)
    spread = 0.002
    return {
        "pair": pair,
        "mid_rate": mid_rate,
        "bid": round(mid_rate * (1 - spread), 6),
        "ask": round(mid_rate * (1 + spread), 6),
        "source": "mock",
    }
