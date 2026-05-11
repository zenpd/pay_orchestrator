"""
FastAPI Backend - Payment Processing Orchestrator
Minimal working version for Streamlit integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Generator, Any
from datetime import datetime
import uvicorn
import threading
from collections import deque

# ============================================================
# MOCK IMPLEMENTATIONS (Replace with your actual code)
# ============================================================

class RealisticPaymentOrchestrator:
    def process_payment(self, payment_data):
        return {
            "payment_id": payment_data["payment_id"],
            "state_key": "test_state_key",
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
            "logs": []
        }

class StateManager:
    def __init__(self):
        self._payments = {}
        self.session_id = "session_123"
    
    def get_session_summary(self):
        return {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "duration_seconds": 3600.0,
            "total_payments": 1,
            "successful": 1,
            "failed": 0,
            "success_rate": 1.0,
            "avg_processing_time": 3.2,
            "rails_used": {"SWIFT_GPI": 1},
            "compliance_stats": {"approved": 1, "hold": 0, "rejected": 0},
            "layer4_stats": {"total_validations": 1, "failures": 0, "success_rate": 1.0}
        }
    
    def reset(self):
        self._payments = {}

class LogCapture:
    def __init__(self):
        self.logs = {}
    
    def create_capture(self, payment_id):
        self.logs[payment_id] = []
    
    def add_log(self, payment_id, message, level):
        if payment_id in self.logs:
            self.logs[payment_id].append({
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            })
    
    def finalize(self, payment_id, status):
        pass
    
    def get_logs(self, payment_id):
        return {"logs": self.logs.get(payment_id, [])}
    
    def clear(self):
        self.logs = {}

# ============================================================
# FASTAPI SETUP
# ============================================================

app = FastAPI(
    title="Payment Processing Orchestrator API",
    version="2.0.0"
)

# CRITICAL: CORS Middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Streamlit to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe log storage
_logs_lock = threading.Lock()
_log_buffer = deque(maxlen=1000)

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
# DEPENDENCIES (Request-scoped)
# ============================================================

def get_orchestrator():
    orchestrator = RealisticPaymentOrchestrator()
    try:
        yield orchestrator
    finally:
        pass

def get_state_manager():
    state_manager = StateManager()
    try:
        yield state_manager
    finally:
        pass

def get_log_capture():
    log_capture = LogCapture()
    try:
        yield log_capture
    finally:
        log_capture.clear()

# ============================================================
# ROUTES
# ============================================================

@app.get("/")
async def root():
    return {"message": "API is running", "status": "OK"}

@app.get("/health")
async def health_check():
    """Health check endpoint - Streamlit checks this"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "payment-orchestrator"
    }

@app.post("/api/v1/payment/process", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentRequest,
    orchestrator: RealisticPaymentOrchestrator = Depends(get_orchestrator),
    log_capture: LogCapture = Depends(get_log_capture),
    state_manager: StateManager = Depends(get_state_manager)
):
    """Process a payment"""
    payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())}"
    
    try:
        # Create log capture
        log_capture.create_capture(payment_id)
        
        # Add logs
        log_capture.add_log(payment_id, "Payment processing started", "INFO")
        
        # Prepare payment data
        payment_data = payment.dict()
        payment_data["payment_id"] = payment_id
        
        # Process
        result = orchestrator.process_payment(payment_data)
        
        # Finalize logs
        log_capture.add_log(payment_id, "Payment completed", "INFO")
        log_capture.finalize(payment_id, "COMPLETED")
        
        # Get logs
        log_data = log_capture.get_logs(payment_id)
        result["logs"] = log_data.get("logs", [])
        
        # Add to global buffer
        with _logs_lock:
            for log in result["logs"]:
                timestamp = datetime.now().strftime("%H:%M:%S")
                _log_buffer.append(f"[{timestamp}] {log.get('message', '')}")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics/session")
async def get_session_metrics(state_manager: StateManager = Depends(get_state_manager)):
    return state_manager.get_session_summary()

@app.get("/api/v1/logs")
async def get_logs(last_n: int = 100):
    """Get recent logs"""
    with _logs_lock:
        logs = list(_log_buffer)[-last_n:]
    return {"logs": logs, "total_logs": len(_log_buffer)}

@app.post("/api/v1/logs/clear")
async def clear_logs():
    """Clear logs"""
    with _logs_lock:
        _log_buffer.clear()
    return {"status": "success"}

@app.post("/api/v1/metrics/reset")
async def reset_metrics(state_manager: StateManager = Depends(get_state_manager)):
    state_manager.reset()
    with _logs_lock:
        _log_buffer.clear()
    return {"status": "success"}

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PAYMENT ORCHESTRATOR API")
    print("=" * 60)
    print("✅ API is ready for Streamlit connection")
    print("📡 API URL: http://localhost:8000")
    print("📊 Health Check: http://localhost:8000/health")
    print("🌐 OpenAPI Docs: http://localhost:8000/docs")
    print("\n🚀 Next: streamlit run your_streamlit_app.py")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")