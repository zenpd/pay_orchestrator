"""
FastAPI Backend - Payment Processing Orchestrator (REQUEST-SCOPED)
RESTful API with request isolation, thread-safe logging, and 5-layer architecture
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Generator, Any
from datetime import datetime
import uvicorn
import logging
import threading
from collections import deque

# Import your existing modules
from payment_orchestrator_mvp import RealisticPaymentOrchestrator
from state_manager import StateManager
from log_capture import LogCapture
from mock_data_sources import MockDataSources

# ============================================================
# FASTAPI APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Payment Processing Orchestrator API",
    description="AI-Powered Payment Orchestration with 5-Layer Architecture (Request-Scoped)",
    version="2.0.0"
)

# CRITICAL: CORS Middleware for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    currency_from: str = Field(..., min_length=3, max_length=3, description="Source currency code")
    currency_to: str = Field(..., min_length=3, max_length=3, description="Target currency code")
    sender_country: str = Field(..., min_length=2, max_length=2, description="Sender country code")
    receiver_country: str = Field(..., min_length=2, max_length=2, description="Receiver country code")
    payment_purpose: str = Field(..., min_length=5, description="Payment purpose/description")
    sender_name: str = Field(..., min_length=2, description="Sender name")
    receiver_name: str = Field(..., min_length=2, description="Receiver name")

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
    logs: List[Dict] = []  # Processing logs for UI display

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
# THREAD-SAFE GLOBAL LOG BUFFER (for Streamlit UI)
# WARNING: For development only - use ELK/CloudWatch in production
# ============================================================

_logs_lock = threading.Lock()
_log_buffer = deque(maxlen=1000)

class StreamlitLogHandler(logging.Handler):
    """Thread-safe log handler for Streamlit UI"""
    def emit(self, record):
        log_entry = self.format(record)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with _logs_lock:
            _log_buffer.append(f"[{timestamp}] {log_entry}")

# Server logging (not payment-specific)
logging.basicConfig(level=logging.INFO)
server_logger = logging.getLogger(__name__)

# Add handler to capture server logs
_buffer_handler = StreamlitLogHandler()
_buffer_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
server_logger.addHandler(_buffer_handler)
logging.getLogger().addHandler(_buffer_handler)

# ============================================================
# REQUEST-SCOPED DEPENDENCIES
# ============================================================

def get_orchestrator() -> Generator[RealisticPaymentOrchestrator, None, None]:
    """
    Creates a new orchestrator instance for each request.
    Ensures complete isolation and thread safety.
    """
    orchestrator = RealisticPaymentOrchestrator()
    try:
        yield orchestrator
    finally:
        # Cleanup if needed
        pass

def get_state_manager() -> Generator[StateManager, None, None]:
    """
    Creates a new state manager instance for each request.
    For production: Replace with database-backed storage.
    """
    state_manager = StateManager()
    try:
        yield state_manager
    finally:
        # Cleanup logic can go here
        pass

def get_log_capture() -> Generator[LogCapture, None, None]:
    """
    Creates a new log capture instance for each request.
    Ensures logs are isolated per payment request.
    """
    log_capture = LogCapture()
    try:
        yield log_capture
    finally:
        # Ensure cleanup after request completes
        log_capture.clear()

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Payment Processing Orchestrator API (Request-Scoped)",
        "version": "2.0.0",
        "architecture": "5-Layer Architecture with AI-Powered Routing",
        "scope": "Request-based isolation (thread-safe)",
        "endpoints": {
            "process_payment": "/api/v1/payment/process",
            "payment_status": "/api/v1/payment/{payment_id}",
            "session_metrics": "/api/v1/metrics/session",
            "logs": "/api/v1/logs",
            "corridors": "/api/v1/corridors",
            "rails": "/api/v1/rails"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - Streamlit verifies this"""
    server_logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "payment-orchestrator",
        "scope": "request-based"
    }

@app.post("/api/v1/payment/process", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentRequest,
    orchestrator: RealisticPaymentOrchestrator = Depends(get_orchestrator),
    log_capture: LogCapture = Depends(get_log_capture),
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    Process a payment through the 5-agent orchestrator with request isolation.
    Each request gets its own orchestrator, log capture, and state manager instances.
    """
    
    # Generate payment ID
    payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())%10000:04d}"
    # payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000:04d}"

    try:
        # Initialize request-specific log capture
        log_capture.create_capture(payment_id)
        
        # Log initial payment request (isolated to this request)
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.add_log(payment_id, f"NEW PAYMENT REQUEST: {payment_id}", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.add_log(payment_id, f"Amount: {payment.currency_from} {payment.amount:,.2f}", "INFO")
        log_capture.add_log(payment_id, f"Corridor: {payment.sender_country} → {payment.receiver_country}", "INFO")
        log_capture.add_log(payment_id, f"Purpose: {payment.payment_purpose}", "INFO")
        log_capture.add_log(payment_id, f"Sender: {payment.sender_name}", "INFO")
        log_capture.add_log(payment_id, f"Receiver: {payment.receiver_name}", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        
        # Prepare payment data for orchestrator
        payment_data = {
            "payment_id": payment_id,
            "amount": payment.amount,
            "currency_from": payment.currency_from,
            "currency_to": payment.currency_to,
            "sender_country": payment.sender_country,
            "receiver_country": payment.receiver_country,
            "payment_purpose": payment.payment_purpose,
            "sender_name": payment.sender_name,
            "receiver_name": payment.receiver_name
        }
        
        log_capture.add_log(payment_id, "🔄 Starting payment processing through orchestrator...", "INFO")
        log_capture.add_log(payment_id, "   Initializing 5-agent workflow...", "INFO")
        
        # Process payment with request-scoped orchestrator
        result = orchestrator.process_payment(payment_data)
        
        # Add completion logs
        status = result.get('status', 'UNKNOWN')
        log_capture.add_log(payment_id, f"✅ Payment processing completed!", "INFO")
        log_capture.add_log(payment_id, f"   Status: {status}", "INFO")
        log_capture.add_log(payment_id, f"   Selected Rail: {result.get('selected_rail', 'NONE')}", "INFO")
        log_capture.add_log(payment_id, f"   Processing Time: {result.get('total_processing_time', 0):.2f}s", "INFO")
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        
        # Finalize log capture
        log_capture.finalize(payment_id, status)
        
        # Get all logs for this request
        log_data = log_capture.get_logs(payment_id)
        
        # Add logs to result
        result["logs"] = log_data.get("logs", [])
        
        # Also add to thread-safe global buffer for Streamlit UI
        with _logs_lock:
            for log_entry in result["logs"]:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                message = log_entry.get('message', '')
                level = log_entry.get('level', 'INFO')
                _log_buffer.append(f"[{timestamp}] {level:7s} - {message}")
        
        return PaymentResponse(**result)
        
    except Exception as e:
        error_msg = f"❌ Payment processing failed: {str(e)}"
        log_capture.add_log(payment_id, error_msg, "ERROR")
        log_capture.add_log(payment_id, f"   Exception type: {type(e).__name__}", "ERROR")
        log_capture.finalize(payment_id, "FAILED")
        
        # Get logs even for failed payments
        log_data = log_capture.get_logs(payment_id)
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": str(e),
                "payment_id": payment_id,
                "logs": log_data.get("logs", [])
            }
        )

@app.get("/api/v1/payment/{payment_id}")
async def get_payment_status(
    payment_id: str,
    state_manager: StateManager = Depends(get_state_manager)
):
    """Get payment status and history (isolated to request scope)"""
    try:
        server_logger.info(f"Status check requested for: {payment_id}")
        
        all_states = state_manager._payments
        matching_states = [
            state for key, state in all_states.items() 
            if state["payment_id"] == payment_id
        ]
        
        if not matching_states:
            server_logger.warning(f"Payment not found: {payment_id}")
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        
        payment_state = matching_states[0]
        server_logger.info(f"Payment {payment_id} status: {payment_state['status']}")
        
        return {
            "payment_id": payment_state["payment_id"],
            "state_key": payment_state["state_key"],
            "status": payment_state["status"],
            "current_stage": payment_state["current_stage"],
            "created_at": payment_state["created_at"],
            "updated_at": payment_state["updated_at"],
            "history": payment_state["history"],
            "data": payment_state["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        server_logger.error(f"Failed to retrieve payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment status: {str(e)}")

@app.get("/api/v1/metrics/session", response_model=SessionMetrics)
async def get_session_metrics(
    state_manager: StateManager = Depends(get_state_manager)
):
    """Get current session metrics (isolated to request)"""
    try:
        server_logger.debug("Session metrics requested")
        summary = state_manager.get_session_summary()
        return SessionMetrics(**summary)
    except Exception as e:
        server_logger.error(f"Failed to retrieve metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")

@app.get("/api/v1/logs")
async def get_logs(last_n: int = 100):
    """
    Get recent logs for UI display (thread-safe).
    WARNING: For development only. Use proper logging service in production.
    """
    try:
        with _logs_lock:
            logs_to_return = list(_log_buffer)[-last_n:] if last_n < len(_log_buffer) else list(_log_buffer)
        return {
            "logs": logs_to_return,
            "total_logs": len(_log_buffer),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        server_logger.error(f"Failed to retrieve logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@app.post("/api/v1/logs/clear")
async def clear_logs():
    """Clear log buffer (thread-safe)"""
    try:
        with _logs_lock:
            _log_buffer.clear()
        server_logger.info("Log buffer cleared")
        return {"status": "success", "message": "Logs cleared"}
    except Exception as e:
        server_logger.error(f"Failed to clear logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

@app.get("/api/v1/corridors")
async def get_corridors(
    sender_country: Optional[str] = None,
    receiver_country: Optional[str] = None
):
    """Get available payment corridors (stateless)"""
    try:
        if sender_country and receiver_country:
            corridor_key = f"{sender_country}_{receiver_country}"
            corridor_data = MockDataSources.get_corridor_metadata(corridor_key)
            
            if not corridor_data or not corridor_data.get("available_rails"):
                return {
                    "corridor": corridor_key,
                    "available": False,
                    "message": "No direct corridor available"
                }
            
            return {
                "corridor": corridor_key,
                "available": True,
                **corridor_data
            }
        else:
            corridors = []
            for corridor_key, data in MockDataSources.CORRIDORS.items():
                corridors.append({
                    "corridor": corridor_key,
                    **data
                })
            return {"corridors": corridors}
            
    except Exception as e:
        server_logger.error(f"Failed to retrieve corridors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve corridors: {str(e)}")

@app.get("/api/v1/rails")
async def get_rails(rail_name: Optional[str] = None):
    """Get payment rail performance metrics (stateless)"""
    try:
        if rail_name:
            rail_data = MockDataSources.get_rail_performance(rail_name)
            if not rail_data:
                raise HTTPException(status_code=404, detail=f"Rail {rail_name} not found")
            return {"rail": rail_name, **rail_data}
        else:
            rails = []
            for rail_name, data in MockDataSources.RAIL_PERFORMANCE.items():
                rails.append({"rail": rail_name, **data})
            return {"rails": rails}
    except HTTPException:
        raise
    except Exception as e:
        server_logger.error(f"Failed to retrieve rail data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rail data: {str(e)}")

@app.get("/api/v1/fx-rate")
async def get_fx_rate(currency_from: str, currency_to: str):
    """Get current FX rate (stateless)"""
    try:
        fx_pair = f"{currency_from}_{currency_to}"
        fx_data = MockDataSources.get_fx_rate(fx_pair)
        return {
            "currency_pair": fx_pair,
            "from": currency_from,
            "to": currency_to,
            **fx_data
        }
    except Exception as e:
        server_logger.error(f"Failed to retrieve FX rate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve FX rate: {str(e)}")

@app.post("/api/v1/metrics/reset")
async def reset_metrics(
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    Reset session metrics (for demo purposes)
    Resets only the request-scoped state manager instance
    """
    try:
        server_logger.info("Resetting session metrics...")
        state_manager.reset()
        
        # Clear global log buffer
        with _logs_lock:
            _log_buffer.clear()
        
        server_logger.info("Session metrics reset successfully")
        return {
            "status": "success",
            "message": "Metrics reset successfully (request-scoped)"
        }
    except Exception as e:
        server_logger.error(f"Failed to reset metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}")

# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  PAYMENT PROCESSING ORCHESTRATOR - API SERVER (REQUEST-SCOPED)")
    print("=" * 80)
    print("\nStarting FastAPI server with request isolation...")
    print("✅ Thread-safe & concurrent-request ready")
    print("✅ Request-scoped dependencies")
    print("✅ Isolated logging per payment")
    print("\n📡 API URL: http://localhost:8000")
    print("📊 Health Check: http://localhost:8000/health")
    print("🌐 OpenAPI Docs: http://localhost:8000/docs")
    print("🌐 Streamlit UI: streamlit run your_streamlit_app.py")
    print("\n" + "=" * 80)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        # For production: workers=4, reload=False
        # For development: reload=True (auto-restart on code changes)
    )