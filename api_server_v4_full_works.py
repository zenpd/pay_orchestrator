"""
FastAPI Backend - Payment Processing Orchestrator (SELF-CONTAINED)
Complete working version with built-in mocks - NO EXTERNAL DEPENDENCIES
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
import uvicorn
import logging
from collections import deque
import threading

# ============================================================
# MOCK IMPLEMENTATIONS (Built-in, no external files needed)
# ============================================================

class MockPaymentOrchestrator:
    """Mock orchestrator that simulates payment processing"""
    
    def process_payment(self, payment_data: dict) -> dict:
        # Simulate 5-agent workflow
        return {
            "payment_id": payment_data["payment_id"],
            "state_key": f"STATE_{payment_data['payment_id']}",
            "status": "COMPLETED",
            "compliance_status": "APPROVED",
            "layer4_validation": "APPROVED",
            "selected_rail": "SWIFT_GPI",
            "backup_rail": "NAMPAY",
            "risk_score": 0.052,
            "actual_cost": 12.50,
            "actual_processing_time": 2.5,
            "success": True,
            "total_processing_time": 3.2,
            "reconciliation_status": "PENDING",
            "logs": []  # Logs added by endpoint
        }

class MockStateManager:
    """Mock state manager for session metrics"""
    
    def __init__(self):
        self._payments = {}
        self.session_id = "session_live"
        self.start_time = datetime.now().isoformat()
    
    def get_session_summary(self) -> dict:
        total = len(self._payments)
        successful = sum(1 for p in self._payments.values() if p.get("status") == "COMPLETED")
        
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "duration_seconds": (datetime.now() - datetime.fromisoformat(self.start_time)).total_seconds(),
            "total_payments": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful / total if total > 0 else 0.0),
            "avg_processing_time": 3.2,  # Mock average
            "rails_used": {"SWIFT_GPI": total},  # Mock rail usage
            "compliance_stats": {"approved": total, "hold": 0, "rejected": 0},
            "layer4_stats": {"total_validations": total, "failures": 0, "success_rate": 1.0}
        }
    
    def reset(self):
        self._payments.clear()
        self.start_time = datetime.now().isoformat()

class MockLogCapture:
    """Mock log capture for payment-specific logs"""
    
    def __init__(self):
        self.logs = {}
    
    def create_capture(self, payment_id: str):
        self.logs[payment_id] = []
    
    def add_log(self, payment_id: str, message: str, level: str = "INFO"):
        if payment_id in self.logs:
            self.logs[payment_id].append({
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            })
    
    def finalize(self, payment_id: str, status: str):
        self.add_log(payment_id, f"Final status: {status}", "INFO")
    
    def get_logs(self, payment_id: str) -> dict:
        return {"logs": self.logs.get(payment_id, [])}
    
    def clear(self):
        self.logs.clear()

class MockDataSources:
    """Mock data for corridors, rails, and FX rates"""
    
    CORRIDORS = {
        "US_GB": {
            "available_rails": ["SWIFT_GPI", "NAMPAY"],
            "compliance_level": "STANDARD",
            "avg_processing_hours": 2.5,
            "daily_volume_limit": 1000000,
            "regulatory_requirements": ["AML_CHECK", "FX_REPORTING"]
        },
        "ZA_US": {
            "available_rails": ["SWIFT_GPI", "BANKSERV"],
            "compliance_level": "HIGH",
            "avg_processing_hours": 4.0,
            "daily_volume_limit": 500000,
            "regulatory_requirements": ["AML_CHECK", "SANCTIONS_CHECK"]
        }
    }
    
    RAIL_PERFORMANCE = {
        "SWIFT_GPI": {
            "success_rate": 0.98,
            "avg_cost_usd": 12.50,
            "avg_processing_time_hours": 2.5,
            "availability": 0.99,
            "last_24h_volume": 150
        },
        "NAMPAY": {
            "success_rate": 0.95,
            "avg_cost_usd": 8.00,
            "avg_processing_time_hours": 1.0,
            "availability": 0.97,
            "last_24h_volume": 200
        }
    }
    
    FX_RATES = {
        "USD_GBP": {"rate": 0.78, "bid": 0.779, "ask": 0.781},
        "ZAR_USD": {"rate": 0.053, "bid": 0.052, "ask": 0.054}
    }
    
    @staticmethod
    def get_corridor_metadata(corridor_key: str):
        return MockDataSources.CORRIDORS.get(corridor_key)
    
    @staticmethod
    def get_rail_performance(rail_name: str):
        return MockDataSources.RAIL_PERFORMANCE.get(rail_name)
    
    @staticmethod
    def get_fx_rate(fx_pair: str):
        return MockDataSources.FX_RATES.get(fx_pair, {"rate": 1.0, "bid": 1.0, "ask": 1.0})

# ============================================================
# GLOBAL SINGLETONS (Simple & Reliable)
# Using global instances like the original working version
# ============================================================

orchestrator = MockPaymentOrchestrator()
state_manager = MockStateManager()
log_capture = MockLogCapture()

# ============================================================
# FASTAPI SETUP
# ============================================================

app = FastAPI(
    title="Payment Processing Orchestrator API",
    description="AI-Powered Payment Orchestration with 5-Layer Architecture",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe log buffer for Streamlit
_log_buffer = deque(maxlen=1000)
_log_lock = threading.Lock()

# ============================================================
# MODELS
# ============================================================

class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency_from: str = Field(..., min_length=3, max_length=3)
    currency_to: str = Field(..., min_length=3, max_length=3)
    sender_country: str = Field(..., min_length=2, max_length=2)
    receiver_country: str = Field(..., min_length=2, max_length=2)
    payment_purpose: str = Field(..., min_length=5)
    sender_name: str = Field(..., min_length=2)
    receiver_name: str = Field(..., min_length=2)

class PaymentResponse(BaseModel):
    payment_id: str
    state_key: str
    status: str
    compliance_status: str
    layer4_validation: str
    selected_rail: str
    backup_rail: str
    risk_score: float
    actual_cost: float
    actual_processing_time: float
    success: bool
    total_processing_time: float
    reconciliation_status: str
    logs: List[Dict] = []

class SessionMetrics(BaseModel):
    session_id: str
    start_time: str
    duration_seconds: float
    total_payments: int
    successful: int
    failed: int
    success_rate: float
    avg_processing_time: float
    rails_used: Dict[str, int]
    compliance_stats: Dict[str, int]
    layer4_stats: Dict[str, float]

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health_check():
    """Health check - Streamlit looks for this"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "payment-orchestrator"
    }

@app.post("/api/v1/payment/process", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """
    Process a payment through the orchestrator
    """
    payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())}"
    
    try:
        # Create log capture for this payment
        log_capture.create_capture(payment_id)
        
        # Log payment details
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.add_log(payment_id, f"NEW PAYMENT REQUEST: {payment_id}", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.add_log(payment_id, f"Amount: {payment.currency_from} {payment.amount:,.2f}", "INFO")
        log_capture.add_log(payment_id, f"Corridor: {payment.sender_country} → {payment.receiver_country}", "INFO")
        log_capture.add_log(payment_id, f"Purpose: {payment.payment_purpose}", "INFO")
        log_capture.add_log(payment_id, f"Sender: {payment.sender_name}", "INFO")
        log_capture.add_log(payment_id, f"Receiver: {payment.receiver_name}", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        
        # Add processing logs
        log_capture.add_log(payment_id, "🔄 Starting payment processing...", "INFO")
        log_capture.add_log(payment_id, "   Agent 1: Context Collector - Gathering FX rates...", "INFO")
        log_capture.add_log(payment_id, "   Agent 2: Policy Reasoner - Validating compliance...", "INFO")
        log_capture.add_log(payment_id, "   Agent 3: Optimizer - Selecting optimal rail...", "INFO")
        log_capture.add_log(payment_id, "   Agent 4: Execution - Processing payment...", "INFO")
        log_capture.add_log(payment_id, "   Agent 5: Feedback - Learning from outcome...", "INFO")
        
        # Process payment
        payment_data = payment.dict()
        payment_data["payment_id"] = payment_id
        
        result = orchestrator.process_payment(payment_data)
        
        # Finalize logs
        log_capture.add_log(payment_id, f"✅ Status: {result['status']}", "INFO")
        log_capture.add_log(payment_id, f"   Selected Rail: {result['selected_rail']}", "INFO")
        log_capture.add_log(payment_id, f"   Processing Time: {result['total_processing_time']:.2f}s", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.finalize(payment_id, result['status'])
        
        # Get logs
        log_data = log_capture.get_logs(payment_id)
        result["logs"] = log_data["logs"]
        
        # Add to global buffer for Streamlit
        with _log_lock:
            for log_entry in result["logs"]:
                timestamp = datetime.now().strftime("%H:%M:%S")
                level = log_entry.get('level', 'INFO')
                msg = log_entry.get('message', '')
                _log_buffer.append(f"[{timestamp}] {level:7s} - {msg}")
        
        return result
        
    except Exception as e:
        log_capture.add_log(payment_id, f"❌ ERROR: {str(e)}", "ERROR")
        log_capture.finalize(payment_id, "FAILED")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics/session")
async def get_session_metrics():
    """Get session metrics"""
    metrics = state_manager.get_session_summary()
    
    # Add current payment count from log captures
    metrics["total_payments"] = len(state_manager._payments)
    
    return metrics

@app.get("/api/v1/logs")
async def get_logs(last_n: int = 100):
    """Get recent logs (thread-safe)"""
    with _log_lock:
        logs = list(_log_buffer)[-last_n:]
    return {
        "logs": logs,
        "total_logs": len(_log_buffer),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/logs/clear")
async def clear_logs():
    """Clear logs"""
    with _log_lock:
        _log_buffer.clear()
    log_capture.clear()
    return {"status": "success", "message": "Logs cleared"}

@app.get("/api/v1/corridors")
async def get_corridors(sender_country: Optional[str] = None, receiver_country: Optional[str] = None):
    """Get payment corridors"""
    if sender_country and receiver_country:
        corridor_key = f"{sender_country}_{receiver_country}"
        data = MockDataSources.get_corridor_metadata(corridor_key)
        if data:
            return {"corridor": corridor_key, "available": True, **data}
        return {"corridor": corridor_key, "available": False, "message": "No direct corridor"}
    
    corridors = []
    for key, data in MockDataSources.CORRIDORS.items():
        corridors.append({"corridor": key, **data})
    return {"corridors": corridors}

@app.get("/api/v1/rails")
async def get_rails(rail_name: Optional[str] = None):
    """Get rail performance"""
    if rail_name:
        data = MockDataSources.get_rail_performance(rail_name)
        if data:
            return {"rail": rail_name, **data}
        raise HTTPException(status_code=404, detail=f"Rail not found")
    
    rails = []
    for name, data in MockDataSources.RAIL_PERFORMANCE.items():
        rails.append({"rail": name, **data})
    return {"rails": rails}

@app.get("/api/v1/fx-rate")
async def get_fx_rate(currency_from: str, currency_to: str):
    """Get FX rate"""
    fx_pair = f"{currency_from}_{currency_to}"
    data = MockDataSources.get_fx_rate(fx_pair)
    return {
        "currency_pair": fx_pair,
        "from": currency_from,
        "to": currency_to,
        **data
    }

@app.post("/api/v1/metrics/reset")
async def reset_metrics():
    """Reset all metrics and logs"""
    state_manager.reset()
    with _log_lock:
        _log_buffer.clear()
    log_capture.clear()
    return {"status": "success", "message": "Session reset"}

# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  PAYMENT PROCESSING ORCHESTRATOR - API SERVER (SELF-CONTAINED)")
    print("=" * 80)
    print("\n✅ ALL MOCKS LOADED - NO EXTERNAL DEPENDENCIES")
    print("✅ GLOBAL STATE - SIMPLE & RELIABLE")
    print("✅ STREAMLIT COMPATIBLE")
    print("\n📡 API URL: http://localhost:8000")
    print("📊 Health Check: http://localhost:8000/health")
    print("\n" + "=" * 80)
    print("\n🚀 STARTING SERVER...\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )