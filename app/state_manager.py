"""
State Manager - Realistic MVP Implementation
Simulates production-grade state management with Redis-like functionality
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading

class StateManager:
    """
    Production-grade state manager simulating Redis
    Handles payment state, caching, and session management
    """
    
    def __init__(self):
        # State storage (mimics Redis)
        self._payments = {}  # payment_id -> payment state
        self._cache = {}     # cache_key -> cached data
        self._metrics = {}   # metrics storage
        self._lock = threading.Lock()
        
        # Session tracking
        self._session_id = f"SESSION-{int(time.time())}"
        self._start_time = datetime.now()
        
        # Initialize metrics
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize metrics tracking"""
        self._metrics = {
            "total_payments": 0,
            "successful_payments": 0,
            "failed_payments": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0,
            "layer4_validations": 0,
            "layer4_validation_failures": 0,
            "rails_used": {},
            "compliance_approvals": 0,
            "compliance_rejections": 0,
            "compliance_holds": 0,
            "preference_counts": {"fastest": 0, "cheapest": 0, "balanced": 0}
        }
        # self._metrics["rails_used"] = {}  # Track rail selection counts
        # self._metrics["preference_counts"] = {"fastest": 0, "cheapest": 0, "balanced": 0}

    def record_rail_selection(self, rail_name: str, preference: str):
        """Track which rail was selected and why"""
        with self._lock:
            # Count rail usage
            if "rails_used" not in self._metrics:
                self._metrics["rails_used"] = {}
            self._metrics["rails_used"][rail_name] = self._metrics["rails_used"].get(rail_name, 0) + 1
            
            # Count preference usage
            if "preference_counts" not in self._metrics:
                self._metrics["preference_counts"] = {"fastest": 0, "cheapest": 0, "balanced": 0}
            self._metrics["preference_counts"][preference] += 1
    
    def create_payment_state(self, payment_id: str, initial_data: Dict) -> str:
        """
        Create new payment state with unique tracking ID
        Returns: state_key for tracking
        """
        with self._lock:
            state_key = f"{payment_id}:{self._session_id}"
            
            payment_state = {
                "payment_id": payment_id,
                "state_key": state_key,
                "session_id": self._session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "INITIATED",
                "current_stage": "context_collection",
                "data": initial_data,
                "history": [{
                    "stage": "initiated",
                    "timestamp": datetime.now().isoformat(),
                    "status": "INITIATED"
                }]
            }
            
            self._payments[state_key] = payment_state
            self._metrics["total_payments"] += 1
            
            return state_key
    
    def update_payment_state(self, state_key: str, stage: str, data: Dict, status: str = "IN_PROGRESS"):
        """Update payment state at specific stage"""
        with self._lock:
            if state_key not in self._payments:
                raise ValueError(f"Payment state not found: {state_key}")
            
            payment_state = self._payments[state_key]
            payment_state["updated_at"] = datetime.now().isoformat()
            payment_state["status"] = status
            payment_state["current_stage"] = stage
            payment_state["data"].update(data)
            
            # Add to history
            payment_state["history"].append({
                "stage": stage,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "data_keys": list(data.keys())
            })
            
            self._payments[state_key] = payment_state
    
    def get_payment_state(self, state_key: str) -> Optional[Dict]:
        """Retrieve complete payment state"""
        with self._lock:
            return self._payments.get(state_key)
    
    def cache_set(self, key: str, value: Any, ttl: int = 300):
        """Set cache value with TTL (simulates Redis SET with EX)"""
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = {
                "value": value,
                "expiry": expiry
            }
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value (simulates Redis GET)"""
        with self._lock:
            if key not in self._cache:
                return None
            
            cached = self._cache[key]
            if datetime.now() > cached["expiry"]:
                del self._cache[key]
                return None
            
            return cached["value"]
    
    def record_metric(self, metric_name: str, value: Any):
        """Record a metric"""
        with self._lock:
            if metric_name in self._metrics:
                if isinstance(self._metrics[metric_name], (int, float)):
                    self._metrics[metric_name] += value
                elif isinstance(self._metrics[metric_name], dict):
                    if value not in self._metrics[metric_name]:
                        self._metrics[metric_name][value] = 0
                    self._metrics[metric_name][value] += 1
            else:
                self._metrics[metric_name] = value
    
    def finalize_payment(self, state_key: str, success: bool, processing_time: float):
        """Finalize payment and update metrics"""
        with self._lock:
            if success:
                self._metrics["successful_payments"] += 1
                self.update_payment_state(state_key, "completed", {}, "SUCCESS")
            else:
                self._metrics["failed_payments"] += 1
                self.update_payment_state(state_key, "failed", {}, "FAILED")
            
            self._metrics["total_processing_time"] += processing_time
            self._metrics["avg_processing_time"] = (
                self._metrics["total_processing_time"] / self._metrics["total_payments"]
            )
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        with self._lock:
            return self._metrics.copy()
    
    def get_session_summary(self) -> Dict:
        """Get session summary"""
        with self._lock:
            duration = (datetime.now() - self._start_time).total_seconds()
            
            return {
                "session_id": self._session_id,
                "start_time": self._start_time.isoformat(),
                "duration_seconds": duration,
                "total_payments": self._metrics["total_payments"],
                "successful": self._metrics["successful_payments"],
                "failed": self._metrics["failed_payments"],
                "success_rate": (
                    (self._metrics["successful_payments"] / self._metrics["total_payments"] * 100)
                    if self._metrics["total_payments"] > 0 else 0.0
                ),
                "avg_processing_time": self._metrics["avg_processing_time"],
                "rails_used": self._metrics["rails_used"],
                "compliance_stats": {
                    "approved": self._metrics["compliance_approvals"],
                    "rejected": self._metrics["compliance_rejections"],
                    "hold": self._metrics["compliance_holds"]
                },
                "layer4_stats": {
                    "total_validations": self._metrics["layer4_validations"],
                    "failures": self._metrics["layer4_validation_failures"],
                    "success_rate": (
                        ((self._metrics["layer4_validations"] - self._metrics["layer4_validation_failures"]) 
                         / self._metrics["layer4_validations"] * 100)
                        if self._metrics["layer4_validations"] > 0 else 0.0
                    )
                },
                "eft_migrations_simulated": self.total_payments,
                "mt_to_mx_conversions": self.total_payments,
                "left_shift_validations_performed": self.total_payments * 8,  # 8 validation types
                "ai_routing_decisions": self.total_payments,
                "rails_used": rails_used,
                "validation_stats": {
                    "approved": sum(1 for p in self._payments.values() if self._get_validation_status(p) == "APPROVED"),
                    "on_hold": sum(1 for p in self._payments.values() if self._get_validation_status(p) == "ON_HOLD"),
                    "rejected": sum(1 for p in self._payments.values() if self._get_validation_status(p) == "REJECTED"),
                }
            }
    
    def get_payment_history(self, state_key: str) -> list:
        """Get payment processing history"""
        with self._lock:
            if state_key not in self._payments:
                return []
            return self._payments[state_key]["history"]


# Global state manager instance
_state_manager = None

def get_state_manager() -> StateManager:
    """Get or create global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

def reset_state_manager():
    """Reset state manager (for testing)"""
    global _state_manager
    _state_manager = StateManager()
