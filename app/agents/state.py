"""Agent state management for payment orchestration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum


class RailType(str, Enum):
    """Supported payment rails."""
    SWIFT_GPI = "SWIFT_GPI"
    NAMPAY = "NAMPAY"
    PARTNER_NETWORK = "PARTNER_NETWORK"
    RTGS_BULK = "RTGS_BULK"
    BATCH_ACH = "BATCH_ACH"
    SLOW_BATCH = "SLOW_BATCH"


@dataclass
class PaymentRequest:
    """Input payment request."""
    session_id: str
    amount: float
    currency: str
    sender_id: str
    receiver_id: str
    corridor: str  # e.g., "ZA_US"
    deadline_minutes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RailScore:
    """Scoring for a single rail."""
    rail_type: RailType
    composite_score: float  # 0-100, higher is better
    cost_score: float
    speed_score: float
    reliability_score: float
    estimated_cost_usd: float
    estimated_time_hours: float
    feasibility: str  # "FEASIBLE", "RISKY", "NOT_FEASIBLE"


@dataclass
class PaymentState:
    """Shared state across agent workflow nodes."""
    session_id: str
    payment_request: PaymentRequest

    # Processing stages
    stage: str  # "analyzing", "scoring", "deciding", "executing", "completed"
    rail_scores: Dict[RailType, RailScore] = field(default_factory=dict)
    selected_rail: Optional[RailType] = None
    execution_result: Optional[Dict[str, Any]] = None

    # Metadata
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "payment_request": self.payment_request.__dict__,
            "stage": self.stage,
            "rail_scores": {k.value: v.__dict__ for k, v in self.rail_scores.items()},
            "selected_rail": self.selected_rail.value if self.selected_rail else None,
            "execution_result": self.execution_result,
            "messages": self.messages,
            "errors": self.errors,
        }
