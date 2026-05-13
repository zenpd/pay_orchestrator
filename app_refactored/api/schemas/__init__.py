"""API schemas for payment orchestration."""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PaymentRequestSchema(BaseModel):
    """Incoming payment request."""
    amount: float = Field(..., gt=0, description="Payment amount in numeric value")
    currency: str = Field(default="USD", description="ISO 4217 currency code")
    sender_id: str = Field(..., description="Sender account/entity identifier")
    receiver_id: str = Field(..., description="Receiver account/entity identifier")
    corridor: str = Field(..., description="Payment corridor, e.g., ZA_US, ZA_GB")
    deadline_minutes: Optional[int] = Field(None, description="Desired completion time")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RailScoreSchema(BaseModel):
    """Rail evaluation score."""
    rail_type: str
    composite_score: float
    cost_score: float
    speed_score: float
    reliability_score: float
    estimated_cost_usd: float
    estimated_time_hours: float
    feasibility: str


class PaymentResponseSchema(BaseModel):
    """Payment orchestration response."""
    session_id: str
    stage: str
    selected_rail: Optional[str] = None
    rail_scores: Dict[str, RailScoreSchema]
    execution_result: Optional[Dict[str, Any]] = None
    messages: List[str]
    errors: List[str]
    created_at: Optional[datetime] = None


class HealthResponseSchema(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
