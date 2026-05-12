"""
FastAPI Backend - Multi-Region Payment Processing Orchestrator
Supports ZA, US, GB, EU regions with region-specific payment rails
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
import uvicorn
import logging
from collections import deque
import threading
import uuid
import traceback
import random
import sys
sys.path.insert(0, '/app')

from config.regions_config import (
    get_region, 
    get_all_regions, 
    get_region_payment_types,
    get_region_rails,
    get_region_corridors,
    get_region_currency
)

# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# PYDANTIC MODELS
# ============================================================

class ComplianceConfig(BaseModel):
    aml_check: bool = True
    sanctions_check: bool = True
    fraud_check: bool = True

class PaymentRequest(BaseModel):
    region: str = Field(..., description="Region code: ZA, US, GB, EU")
    payment_type: str = Field(..., description="Payment type for the selected region")
    amount: float = Field(..., gt=0, description="Payment amount")
    sender_country: str = Field(..., min_length=2, max_length=2)
    receiver_country: str = Field(..., min_length=2, max_length=2)
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    sender_account: str = Field(..., description="Sender account number")
    receiver_account: str = Field(..., description="Receiver account number")
    optimization: str = Field(default="Balanced", description="Speed-Focused, Cost-Focused, or Balanced")
    risk_tolerance: str = Field(default="Medium", description="Risk tolerance level")
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)

class PaymentResponse(BaseModel):
    status: str
    payment_id: str
    region: str
    payment_type: str
    amount: float
    selected_rail: str
    processing_time_ms: int
    compliance_status: str
    route_score: float
    estimated_cost: float
    rails_considered: List[Dict[str, Any]]
    execution_details: Dict[str, Any]

# ============================================================
# LOG CAPTURE (Thread-Safe)
# ============================================================

class LogCapture:
    def __init__(self):
        self.logs: Dict[str, deque] = {}
        self.lock = threading.Lock()
    
    def add_log(self, payment_id: str, message: str, level: str = "INFO"):
        with self.lock:
            if payment_id not in self.logs:
                self.logs[payment_id] = deque(maxlen=100)
            
            self.logs[payment_id].append({
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            })
    
    def get_logs(self, payment_id: str) -> List[Dict]:
        with self.lock:
            return list(self.logs.get(payment_id, []))
    
    def clear_logs(self):
        with self.lock:
            self.logs.clear()

log_capture = LogCapture()

# ============================================================
# REGION-AWARE RAIL SELECTION
# ============================================================

class RegionalRailSelector:
    """AI-based rail selection per region"""
    
    def __init__(self):
        self.selection_history = []
    
    def calculate_rail_score(self, rail_config: Dict, optimization: str, amount: float, processing_time: str) -> float:
        """Calculate composite score for a rail"""
        score = 0
        
        # Speed component
        speed_weight = 0.5 if optimization == "Speed-Focused" else 0.3
        speed_score = rail_config.get("speed_score", 50)
        score += speed_score * speed_weight
        
        # Cost component
        cost_weight = 0.5 if optimization == "Cost-Focused" else 0.3
        cost_score = rail_config.get("cost_score", 50)
        score += cost_score * cost_weight
        
        # Availability component
        availability = rail_config.get("availability", 0.95)
        score += (availability * 100) * 0.2
        
        # Amount compatibility
        max_amount = rail_config.get("max_amount", float('inf'))
        if amount <= max_amount:
            score += 10
        
        # Risk adjustment
        risk_map = {"VERY_LOW": 20, "LOW": 15, "MEDIUM": 10, "HIGH": 5}
        risk_bonus = risk_map.get(rail_config.get("risk_level", "MEDIUM"), 0)
        score += risk_bonus * 0.1
        
        return round(score, 2)
    
    def select_rail(self, region: str, payment_type: str, amount: float, optimization: str) -> Dict[str, Any]:
        """Select best rail for the given criteria"""
        try:
            region_config = get_region(region)
            region_rails = region_config.get("rails", {})
            
            if not region_rails:
                raise ValueError(f"No rails configured for region {region}")
            
            # Calculate scores for all rails
            rail_scores = []
            for rail_name, rail_config in region_rails.items():
                score = self.calculate_rail_score(
                    rail_config,
                    optimization,
                    amount,
                    rail_config.get("processing_time", "Unknown")
                )
                
                rail_scores.append({
                    "rail": rail_name,
                    "score": score,
                    "type": rail_config.get("type", "Unknown"),
                    "speed": rail_config.get("processing_time", "Unknown"),
                    "cost": f"${rail_config.get('avg_cost_usd', 0):.2f}",
                    "availability": f"{rail_config.get('availability', 0.95)*100:.1f}%"
                })
            
            # Sort by score descending
            rail_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Select top rail
            selected = rail_scores[0] if rail_scores else None
            
            if not selected:
                raise ValueError("No suitable rail found")
            
            # Log selection
            self.selection_history.append({
                "timestamp": datetime.now().isoformat(),
                "region": region,
                "payment_type": payment_type,
                "amount": amount,
                "selected_rail": selected["rail"],
                "score": selected["score"]
            })
            
            return {
                "selected_rail": selected["rail"],
                "score": selected["score"],
                "all_rails_scored": rail_scores
            }
        
        except Exception as e:
            logger.error(f"Rail selection error: {str(e)}")
            # Fallback to random rail
            region_rails = get_region_rails(region)
            fallback_rail = random.choice(list(region_rails.keys()))
            return {
                "selected_rail": fallback_rail,
                "score": 0,
                "all_rails_scored": [],
                "fallback": True,
                "error": str(e)
            }

rail_selector = RegionalRailSelector()

# ============================================================
# MOCK PROCESSOR
# ============================================================

class PaymentProcessor:
    """Mock payment processor"""
    
    @staticmethod
    def validate_region(region: str) -> bool:
        """Validate region code"""
        try:
            get_region(region)
            return True
        except:
            return False
    
    @staticmethod
    def validate_compliance(payment: PaymentRequest, region: str) -> Dict[str, Any]:
        """Mock compliance validation"""
        compliance_checks = {
            "aml_check": "PASSED" if payment.compliance.aml_check else "SKIPPED",
            "sanctions_check": "PASSED" if payment.compliance.sanctions_check else "SKIPPED",
            "fraud_check": "PASSED" if payment.compliance.fraud_check else "SKIPPED"
        }
        
        all_passed = all(v == "PASSED" or v == "SKIPPED" for v in compliance_checks.values())
        
        return {
            "status": "APPROVED" if all_passed else "REJECTED",
            "checks": compliance_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_cost(rail_name: str, region: str, amount: float) -> float:
        """Calculate estimated cost"""
        try:
            rail_config = get_region_rails(region).get(rail_name, {})
            base_cost = rail_config.get("avg_cost_usd", 10.0)
            
            # Add percentage fee for high amounts
            if amount > 100000:
                base_cost += (amount / 100000) * 5
            
            return round(base_cost, 2)
        except:
            return random.uniform(0.5, 30.0)

processor = PaymentProcessor()

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Payment Orchestrator API - Multi-Region",
    description="AI-driven payment routing across global regions",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/regions", tags=["Configuration"])
async def get_regions_endpoint():
    """Get all available regions"""
    try:
        regions = get_all_regions()
        return {"status": "success", "regions": regions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/regions/{region_code}/payment-types", tags=["Configuration"])
async def get_region_payment_types_endpoint(region_code: str):
    """Get payment types for a region"""
    try:
        payment_types = get_region_payment_types(region_code)
        return {
            "status": "success",
            "region": region_code,
            "payment_types": list(payment_types.keys()),
            "count": len(payment_types)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/regions/{region_code}/rails", tags=["Configuration"])
async def get_region_rails_endpoint(region_code: str):
    """Get available rails for a region"""
    try:
        rails = get_region_rails(region_code)
        rail_summary = {
            name: {
                "type": config.get("type"),
                "speed_score": config.get("speed_score"),
                "cost_score": config.get("cost_score"),
                "processing_time": config.get("processing_time", "Unknown")
            }
            for name, config in rails.items()
        }
        return {
            "status": "success",
            "region": region_code,
            "rails": rail_summary,
            "count": len(rails)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process-payment", response_model=PaymentResponse, tags=["Payments"])
async def process_payment(payment: PaymentRequest):
    """Process a payment with region-aware rail selection"""
    
    payment_id = str(uuid.uuid4())[:12]
    start_time = datetime.now()
    
    try:
        log_capture.add_log(payment_id, f"Starting payment processing for region {payment.region}")
        
        # Validate region
        if not processor.validate_region(payment.region):
            raise ValueError(f"Invalid region: {payment.region}")
        
        log_capture.add_log(payment_id, f"Region {payment.region} validated")
        
        # Compliance check
        compliance_result = processor.validate_compliance(payment, payment.region)
        log_capture.add_log(payment_id, f"Compliance check: {compliance_result['status']}")
        
        if compliance_result["status"] == "REJECTED":
            raise ValueError("Compliance check failed")
        
        # Select optimal rail
        log_capture.add_log(payment_id, f"Starting rail selection with optimization: {payment.optimization}")
        
        rail_selection = rail_selector.select_rail(
            region=payment.region,
            payment_type=payment.payment_type,
            amount=payment.amount,
            optimization=payment.optimization
        )
        
        selected_rail = rail_selection["selected_rail"]
        log_capture.add_log(payment_id, f"Selected rail: {selected_rail} with score {rail_selection['score']}")
        
        # Calculate cost
        estimated_cost = processor.calculate_cost(selected_rail, payment.region, payment.amount)
        log_capture.add_log(payment_id, f"Estimated cost: ${estimated_cost:.2f}")
        
        # Mock execution
        processing_time_ms = random.randint(500, 5000)
        
        # Build response
        processing_time = datetime.now() - start_time
        
        response = PaymentResponse(
            status="SUCCESS",
            payment_id=payment_id,
            region=payment.region,
            payment_type=payment.payment_type,
            amount=payment.amount,
            selected_rail=selected_rail,
            processing_time_ms=processing_time_ms,
            compliance_status=compliance_result["status"],
            route_score=rail_selection["score"],
            estimated_cost=estimated_cost,
            rails_considered=rail_selection.get("all_rails_scored", [])[:5],
            execution_details={
                "optimization": payment.optimization,
                "risk_tolerance": payment.risk_tolerance,
                "compliance_checks": compliance_result["checks"],
                "currency_pair": f"{payment.from_currency}/{payment.to_currency}",
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        log_capture.add_log(payment_id, "Payment processing completed successfully", "SUCCESS")
        return response
    
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}\n{traceback.format_exc()}")
        log_capture.add_log(payment_id, f"Error: {str(e)}", "ERROR")
        
        raise HTTPException(
            status_code=400,
            detail=f"Payment processing failed: {str(e)}"
        )

@app.get("/logs/{payment_id}", tags=["Debugging"])
async def get_payment_logs(payment_id: str):
    """Get logs for a payment"""
    logs = log_capture.get_logs(payment_id)
    return {"payment_id": payment_id, "logs": logs, "count": len(logs)}

@app.delete("/logs", tags=["Debugging"])
async def clear_logs():
    """Clear all logs"""
    log_capture.clear_logs()
    return {"status": "success", "message": "All logs cleared"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "regions_available": len(get_all_regions()),
        "api_version": "2.0.0"
    }

@app.get("/", tags=["Info"])
async def root():
    """API information"""
    return {
        "name": "Payment Orchestrator API - Multi-Region",
        "version": "2.0.0",
        "description": "AI-driven payment routing across ZA, US, GB, EU regions",
        "endpoints": {
            "regions": "/regions",
            "payment_types": "/regions/{region_code}/payment-types",
            "rails": "/regions/{region_code}/rails",
            "process_payment": "/process-payment",
            "health": "/health"
        }
    }

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
