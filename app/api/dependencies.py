"""Dependency injection and shared dependencies."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import get_session


async def get_db_session() -> AsyncSession:
    """Get database session for route handlers."""
    async for session in get_session():
        yield session
