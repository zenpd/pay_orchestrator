from __future__ import annotations
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Numeric, String, Text, text
from db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(64), primary_key=True)
    payment_id = Column(String(64), nullable=False, unique=True, index=True)
    state_key = Column(String(128), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    currency_from = Column(String(3), nullable=False)
    currency_to = Column(String(3), nullable=False)
    sender_country = Column(String(3), nullable=False)
    receiver_country = Column(String(3), nullable=False)
    sender_name = Column(String(140), nullable=False)
    receiver_name = Column(String(140), nullable=False)
    payment_purpose = Column(String(280), nullable=True)
    routing_preference = Column(String(20), nullable=True, server_default="balanced")
    compliance_status = Column(String(30), nullable=True)
    risk_score = Column(Float(), nullable=True)
    selected_rail = Column(String(40), nullable=True)
    execution_status = Column(String(30), nullable=True)
    execution_time = Column(Float(), nullable=True)
    actual_cost = Column(Float(), nullable=True)
    actual_processing_time = Column(Float(), nullable=True)
    success = Column(Boolean(), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))


class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_log"

    id = Column(String(64), primary_key=True)
    payment_id = Column(String(64), ForeignKey("payments.payment_id"), nullable=False, index=True)
    stage = Column(String(40), nullable=False)
    status = Column(String(30), nullable=False)
    details = Column(Text(), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=text("now()"))


class ComplianceDecision(Base):
    __tablename__ = "compliance_decisions"

    id = Column(String(64), primary_key=True)
    payment_id = Column(String(64), ForeignKey("payments.payment_id"), nullable=False, index=True)
    decision = Column(String(30), nullable=False)
    officer_id = Column(String(64), nullable=True)
    notes = Column(Text(), nullable=True)
    decided_at = Column(DateTime(timezone=True), server_default=text("now()"))
