from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class ProcessPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount in source currency")
    currency_from: str = Field(..., min_length=3, max_length=3, description="ISO 4217 source currency")
    currency_to: str = Field(..., min_length=3, max_length=3, description="ISO 4217 destination currency")
    sender_country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 sender country")
    receiver_country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 receiver country")
    sender_name: str = Field(..., min_length=1, max_length=140)
    receiver_name: str = Field(..., min_length=1, max_length=140)
    payment_purpose: str = Field("", max_length=280)
    routing_preference: Literal["fastest", "cheapest", "balanced"] = "balanced"
    urgency: int = Field(5, ge=1, le=10, description="Urgency level 1–10")
    risk_tolerance: int = Field(5, ge=1, le=10, description="Risk tolerance 1–10")
