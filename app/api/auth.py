"""Authentication and authorization utilities."""
from __future__ import annotations

from fastapi import HTTPException, status


def validate_api_key(api_key: str) -> bool:
    """Validate API key for request authentication."""
    # Mock implementation — in production, validate against Key Vault or database
    return len(api_key) > 0
