"""Database models and session management."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, Enum
from datetime import datetime
import enum

from config.settings import get_settings

Base = declarative_base()
settings = get_settings()


class PaymentStatus(str, enum.Enum):
    """Payment processing status states."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentRailType(str, enum.Enum):
    """Supported payment rails."""
    SWIFT_GPI = "SWIFT_GPI"
    NAMPAY = "NAMPAY"
    PARTNER_NETWORK = "PARTNER_NETWORK"
    RTGS_BULK = "RTGS_BULK"
    BATCH_ACH = "BATCH_ACH"
    SLOW_BATCH = "SLOW_BATCH"


class Payment(Base):
    """Payment order model."""
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    sender_id = Column(String(50), nullable=False)
    receiver_id = Column(String(50), nullable=False)
    corridor = Column(String(20), nullable=False)  # e.g., "ZA_US"
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    selected_rail = Column(Enum(PaymentRailType), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)


class RailEvaluation(Base):
    """Rail scoring and evaluation results."""
    __tablename__ = "rail_evaluations"

    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), nullable=False)
    rail_type = Column(Enum(PaymentRailType), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    cost_score = Column(Float, nullable=False)
    speed_score = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database engine and session factory
engine = None
SessionLocal = None


async def init_db() -> None:
    """Initialize database engine and session factory."""
    global engine, SessionLocal

    engine = create_async_engine(
        settings.database_url,
        echo=(settings.app_env == "development"),
    )

    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a database session for dependency injection."""
    if SessionLocal is None:
        await init_db()

    async with SessionLocal() as session:
        yield session
