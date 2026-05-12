from __future__ import annotations
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from shared.config import get_settings

settings = get_settings()
_bearer = HTTPBearer(auto_error=False)
ALGORITHMS = ["RS256"]


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    url = f"{settings.entra_authority}{settings.azure_tenant_id}/discovery/v2.0/keys"
    r = httpx.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if settings.app_env == "development":
        return {"sub": "dev-user", "roles": ["admin"]}
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = jwt.decode(
            credentials.credentials,
            _get_jwks(),
            algorithms=ALGORITHMS,
            audience=settings.entra_audience,
            options={"verify_at_hash": False},
        )
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
