"""
FastAPI Backend - Payment Processing Orchestrator (ENHANCED)
Multi-rail AI selection with intelligent scoring
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

# ============================================================
# ENHANCED MOCK IMPLEMENTATIONS
# ============================================================

class MockDataSources:
    """Enhanced mock data with detailed rail attributes"""
    
    # Detailed rail definitions with scoring attributes
    RAILS = {
        "SWIFT_GPI": {
            "type": "CROSS_BORDER",
            "success_rate": 0.98,
            "avg_cost_usd": 12.50,
            "speed_score": 75,  # 0-100
            "cost_score": 40,   # Higher = cheaper
            "max_amount": 10000000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 500,
            "availability": 0.995,
            "supported_corridors": ["ZA_US", "US_GB", "ZA_GB"]
        },
        "NAMPAY": {
            "type": "CROSS_BORDER",
            "success_rate": 0.95,
            "avg_cost_usd": 8.00,
            "speed_score": 85,
            "cost_score": 70,
            "max_amount": 500000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 1000,
            "availability": 0.97,
            "supported_corridors": ["US_GB", "ZA_US"]
        },
        "PARTNER_NETWORK": {
            "type": "CROSS_BORDER",
            "success_rate": 0.92,
            "avg_cost_usd": 6.00,
            "speed_score": 65,
            "cost_score": 85,
            "max_amount": 200000,
            "risk_level": "HIGH",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 2000,
            "availability": 0.95,
            "supported_corridors": ["ZA_US", "ZA_GB"]
        },
        "RTGS_BULK": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.99,
            "avg_cost_usd": 0.50,
            "speed_score": 30,  # EOD batch
            "cost_score": 95,   # Very cheap for bulk
            "max_amount": 10000000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 100000,  # Bulk processing
            "availability": 0.999,
            "supported_corridors": ["ZA_ZA"]
        },
        "BATCH_ACH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.96,
            "avg_cost_usd": 0.20,
            "speed_score": 40,  # 4-hour batches
            "cost_score": 98,   # Cheapest
            "max_amount": 500000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 50000,
            "availability": 0.98,
            "supported_corridors": ["ZA_ZA"]
        },
        "SLOW_BATCH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.94,
            "avg_cost_usd": 0.10,
            "speed_score": 20,  # Next day
            "cost_score": 100,  # Cheapest possible
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 20000,
            "availability": 0.97,
            "supported_corridors": ["ZA_ZA"]
        },
        "PayShap_INSTANT": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.97,
            "avg_cost_usd": 0.30,
            "speed_score": 100,  # ~3.6 seconds
            "cost_score": 80,
            "max_amount": 50000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 5000,
            "availability": 0.99,
            "supported_corridors": ["ZA_ZA"]
        },
        "RTGS_REALTIME": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.99,
            "avg_cost_usd": 2.50,
            "speed_score": 90,  # ~5 seconds
            "cost_score": 50,
            "max_amount": 5000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 1000,
            "availability": 0.998,
            "supported_corridors": ["ZA_ZA"]
        },
        "CARD_RAIL": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.93,
            "avg_cost_usd": 1.50,
            "speed_score": 95,  # ~4 seconds
            "cost_score": 60,
            "max_amount": 10000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 8000,
            "availability": 0.96,
            "supported_corridors": ["ZA_ZA"]
        },
        "PayShap_SCHEDULED": {
            "type": "DOMESTIC_SCHEDULED",
            "success_rate": 0.98,
            "avg_cost_usd": 0.25,
            "speed_score": 50,  # 4-hour batch
            "cost_score": 90,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 10000,
            "availability": 0.99,
            "supported_corridors": ["ZA_ZA"]
        },
        "STANDING_ORDER": {
            "type": "DOMESTIC_SCHEDULED",
            "success_rate": 0.99,
            "avg_cost_usd": 0.15,
            "speed_score": 45,  # Scheduled batch
            "cost_score": 95,
            "max_amount": 50000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "VERY_LOW",
            "capacity_per_hour": 5000,
            "availability": 0.995,
            "supported_corridors": ["ZA_ZA"]
        },
        "SADC_PAY": {
            "type": "REGIONAL",
            "success_rate": 0.94,
            "avg_cost_usd": 5.00,
            "speed_score": 70,
            "cost_score": 65,
            "max_amount": 200000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 2000,
            "availability": 0.96,
            "supported_corridors": ["ZA_BW", "ZA_ZW", "ZA_MZ"]
        },
        "REGIONAL_PARTNER": {
            "type": "REGIONAL",
            "success_rate": 0.90,
            "avg_cost_usd": 3.50,
            "speed_score": 60,
            "cost_score": 75,
            "max_amount": 100000,
            "risk_level": "HIGH",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 1500,
            "availability": 0.93,
            "supported_corridors": ["ZA_BW", "ZA_ZW"]
        },
        # US Rails
        "ACH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.99,
            "avg_cost_usd": 0.25,
            "speed_score": 40,
            "cost_score": 95,
            "max_amount": 25000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 50000,
            "availability": 0.999,
            "supported_corridors": ["US_US"]
        },
        "RTP": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.98,
            "avg_cost_usd": 0.50,
            "speed_score": 95,
            "cost_score": 70,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 10000,
            "availability": 0.998,
            "supported_corridors": ["US_US"]
        },
        "FedWire": {
            "type": "CROSS_BORDER",
            "success_rate": 0.998,
            "avg_cost_usd": 15.00,
            "speed_score": 90,
            "cost_score": 30,
            "max_amount": 10000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 100,
            "availability": 0.9999,
            "supported_corridors": ["US_US", "US_MX"]
        },
        "WIRE": {
            "type": "CROSS_BORDER",
            "success_rate": 0.97,
            "avg_cost_usd": 20.00,
            "speed_score": 85,
            "cost_score": 25,
            "max_amount": 5000000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 500,
            "availability": 0.99,
            "supported_corridors": ["US_US", "US_MX"]
        },
        "RIPPLE": {
            "type": "CROSS_BORDER",
            "success_rate": 0.95,
            "avg_cost_usd": 5.00,
            "speed_score": 92,
            "cost_score": 80,
            "max_amount": 1000000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 5000,
            "availability": 0.97,
            "supported_corridors": ["US_MX"]
        },
        # UK Rails
        "FPS": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.99,
            "avg_cost_usd": 0.15,
            "speed_score": 98,
            "cost_score": 85,
            "max_amount": 250000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 20000,
            "availability": 0.999,
            "supported_corridors": ["GB_GB"]
        },
        "CHAPS": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.998,
            "avg_cost_usd": 25.00,
            "speed_score": 85,
            "cost_score": 20,
            "max_amount": 10000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500,
            "availability": 0.9999,
            "supported_corridors": ["GB_GB"]
        },
        "Bacs": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.99,
            "avg_cost_usd": 0.20,
            "speed_score": 30,
            "cost_score": 90,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 100000,
            "availability": 0.999,
            "supported_corridors": ["GB_GB"]
        },
        # EU Rails
        "SEPA_CREDIT": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.99,
            "avg_cost_usd": 0.35,
            "speed_score": 50,
            "cost_score": 88,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 50000,
            "availability": 0.999,
            "supported_corridors": ["EU_EU", "GB_EU", "EU_UK"]
        },
        "SEPA_INSTANT": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.98,
            "avg_cost_usd": 0.75,
            "speed_score": 99,
            "cost_score": 70,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 10000,
            "availability": 0.998,
            "supported_corridors": ["EU_EU"]
        },
        "TARGET2": {
            "type": "CROSS_BORDER",
            "success_rate": 0.999,
            "avg_cost_usd": 5.00,
            "speed_score": 95,
            "cost_score": 60,
            "max_amount": 50000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 1000,
            "availability": 0.9999,
            "supported_corridors": ["EU_EU", "GB_EU"]
        },
        # Multi-region Rails
        "Money_Transfer": {
            "type": "CROSS_BORDER",
            "success_rate": 0.95,
            "avg_cost_usd": 8.00,
            "speed_score": 70,
            "cost_score": 75,
            "max_amount": 500000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 5000,
            "availability": 0.98,
            "supported_corridors": ["GB_WW"]
        },
        "Correspondent": {
            "type": "CROSS_BORDER",
            "success_rate": 0.92,
            "avg_cost_usd": 30.00,
            "speed_score": 55,
            "cost_score": 10,
            "max_amount": 2000000,
            "risk_level": "HIGH",
            "regulatory_overhead": "VERY_HIGH",
            "capacity_per_hour": 200,
            "availability": 0.85,
            "supported_corridors": ["GB_WW", "EU_UK"]
        }
    }
    
    CORRIDORS = {
        "ZA_US": {
            "available_rails": ["SWIFT_GPI", "NAMPAY", "PARTNER_NETWORK"],
            "compliance_level": "HIGH",
            "regulatory_req": ["AML", "SANCTIONS", "FX_REPORTING"]
        },
        "ZA_ZA": {
            "available_rails": ["RTGS_BULK", "BATCH_ACH", "SLOW_BATCH", 
                               "PayShap_INSTANT", "RTGS_REALTIME", "CARD_RAIL",
                               "PayShap_SCHEDULED", "STANDING_ORDER"],
            "compliance_level": "STANDARD",
            "regulatory_req": ["AML"]
        },
        "ZA_BW": {
            "available_rails": ["SADC_PAY", "SWIFT_GPI", "REGIONAL_PARTNER"],
            "compliance_level": "REGIONAL",
            "regulatory_req": ["AML", "SADC_COMPLIANCE"]
        },
        "US_US": {
            "available_rails": ["ACH", "RTP", "FedWire", "WIRE"],
            "compliance_level": "STANDARD",
            "regulatory_req": ["AML", "OFAC"]
        },
        "US_MX": {
            "available_rails": ["SWIFT_GPI", "RIPPLE", "WIRE", "FedWire"],
            "compliance_level": "HIGH",
            "regulatory_req": ["AML", "SANCTIONS", "FX_REPORTING"]
        },
        "GB_GB": {
            "available_rails": ["FPS", "CHAPS", "Bacs"],
            "compliance_level": "STANDARD",
            "regulatory_req": ["AML"]
        },
        "GB_EU": {
            "available_rails": ["SWIFT_GPI", "SEPA_CREDIT", "TARGET2"],
            "compliance_level": "HIGH",
            "regulatory_req": ["AML", "BREXIT_COMPLIANCE"]
        },
        "GB_WW": {
            "available_rails": ["SWIFT_GPI", "Money_Transfer", "Correspondent"],
            "compliance_level": "HIGH",
            "regulatory_req": ["AML", "SANCTIONS"]
        },
        "EU_EU": {
            "available_rails": ["SEPA_CREDIT", "SEPA_INSTANT", "TARGET2", "SWIFT_GPI"],
            "compliance_level": "STANDARD",
            "regulatory_req": ["AML"]
        },
        "EU_UK": {
            "available_rails": ["SWIFT_GPI", "SEPA_CREDIT", "Correspondent"],
            "compliance_level": "HIGH",
            "regulatory_req": ["AML", "BREXIT_COMPLIANCE"]
        }
    }
    
    @staticmethod
    def get_rail(rail_name: str):
        return MockDataSources.RAILS.get(rail_name)
    
    @staticmethod
    def get_corridor(corridor_key: str):
        return MockDataSources.CORRIDORS.get(corridor_key)
    
    @staticmethod
    def calculate_fx_rate(from_curr: str, to_curr: str):
        # Mock FX rates
        rates = {
            # ZAR pairs
            ("ZAR", "USD"): 0.053,
            ("USD", "ZAR"): 18.85,
            ("ZAR", "GBP"): 0.041,
            ("GBP", "ZAR"): 24.20,
            ("ZAR", "BWP"): 0.72,  # Botswana Pula
            ("BWP", "ZAR"): 1.38,
            # USD pairs
            ("USD", "GBP"): 0.78,
            ("GBP", "USD"): 1.28,
            ("USD", "EUR"): 0.92,
            ("EUR", "USD"): 1.09,
            ("USD", "MXN"): 16.80,
            ("MXN", "USD"): 0.0595,
            # GBP pairs
            ("GBP", "EUR"): 1.18,
            ("EUR", "GBP"): 0.85,
            # EUR pairs
            ("EUR", "EUR"): 1.0,
            # Same currency pairs
            ("USD", "USD"): 1.0,
            ("GBP", "GBP"): 1.0,
            ("ZAR", "ZAR"): 1.0,
            ("MXN", "MXN"): 1.0
        }
        return rates.get((from_curr, to_curr), 1.0)

class MockPaymentOrchestrator:
    """Enhanced orchestrator with real AI scoring logic"""
    
    def __init__(self):
        self.state_manager = MockStateManager()
    
    def score_rail(self, rail_name: str, payment_data: dict) -> dict:
        """Calculate weighted score for a rail"""
        rail = MockDataSources.get_rail(rail_name)
        if not rail:
            return None
        
        # Check corridor support
        corridor = f"{payment_data['sender_country']}_{payment_data['receiver_country']}"
        if corridor not in rail['supported_corridors']:
            return None
        
        # Check capacity
        amount = payment_data['amount']
        capacity_ok = amount <= rail['max_amount']
        if not capacity_ok:
            return None
        
        # Base scores
        speed_score = rail['speed_score']
        cost_score = rail['cost_score']
        
        # Preference weighting
        preference = payment_data.get('routing_preference', 'balanced')
        urgency = payment_data.get('urgency', 5)
        risk_tolerance = payment_data.get('risk_tolerance', 7)
        
        if preference == 'fastest':
            # High urgency boosts speed importance
            speed_weight = 0.7 + (urgency / 50)  # 0.7-0.9
            cost_weight = 1 - speed_weight
        elif preference == 'cheapest':
            # High risk tolerance boosts cost importance
            cost_weight = 0.7 + (risk_tolerance / 50)  # 0.7-0.9
            speed_weight = 1 - cost_weight
        else:  # balanced
            speed_weight = 0.5 + (urgency / 100) - (risk_tolerance / 200)
            cost_weight = 1 - speed_weight
        
        # Calculate weighted base score
        base_score = (speed_score * speed_weight) + (cost_score * cost_weight)
        
        # Apply penalties
        risk_penalties = {"VERY_LOW": 0, "LOW": 5, "MEDIUM": 15, "HIGH": 30}
        reg_penalties = {"VERY_LOW": 0, "LOW": 3, "MEDIUM": 8, "HIGH": 15}
        
        risk_penalty = risk_penalties.get(rail['risk_level'], 10)
        reg_penalty = reg_penalties.get(rail['regulatory_overhead'], 5)
        
        # Higher risk tolerance reduces penalty impact
        risk_penalty = risk_penalty * (1 - risk_tolerance / 15)
        
        final_score = base_score - risk_penalty - reg_penalty
        
        return {
            'rail': rail_name,
            'final_score': max(0, final_score),
            'base_score': base_score,
            'speed_score': speed_score,
            'cost_score': cost_score,
            'risk_penalty': risk_penalty,
            'regulatory_penalty': reg_penalty,
            'capacity_ok': capacity_ok,
            'risk_level': rail['risk_level'],
            'regulatory_overhead': rail['regulatory_overhead'],
            'speed_weight': speed_weight,
            'cost_weight': cost_weight,
            'actual_cost_usd': rail['avg_cost_usd']
        }
    
    def select_optimal_rail(self, payment_data: dict, available_rails: list) -> dict:
        """AI rail selection with scoring and justification"""
        scored_rails = []
        
        for rail_name in available_rails:
            score_data = self.score_rail(rail_name, payment_data)
            if score_data:
                scored_rails.append(score_data)
        
        if not scored_rails:
            return {
                'selected': None,
                'runner_up': None,
                'all_scored_rails': [],
                'justification': "No suitable rails available"
            }
        
        # Sort by final score
        scored_rails.sort(key=lambda x: x['final_score'], reverse=True)
        
        selected = scored_rails[0]
        runner_up = scored_rails[1] if len(scored_rails) > 1 else None
        
        # Generate justification
        if selected['speed_score'] > selected['cost_score'] and payment_data.get('urgency', 5) > 6:
            reason = "Highest speed score matches urgent payment requirement"
        elif selected['cost_score'] > selected['speed_score'] and payment_data.get('routing_preference') == 'cheapest':
            reason = "Best cost efficiency matches customer preference"
        elif selected['risk_level'] in ['VERY_LOW', 'LOW'] and payment_data.get('risk_tolerance', 7) < 5:
            reason = "Lowest risk level preferred for risk-averse customer"
        else:
            reason = "Best overall weighted score based on your preferences"
        
        return {
            'selected': {
                'rail': selected['rail'],
                'score': round(selected['final_score'], 2),
                'attributes': {
                    'speed_score': selected['speed_score'],
                    'cost_score': selected['cost_score'],
                    'risk_level': selected['risk_level'],
                    'regulatory_overhead': selected['regulatory_overhead'],
                    'capacity_ok': selected['capacity_ok']
                }
            },
            'runner_up': {
                'rail': runner_up['rail'],
                'score': round(runner_up['final_score'], 2),
                'margin': round(selected['final_score'] - runner_up['final_score'], 2),
                'reason': "Lower weighted score"
            } if runner_up else None,
            'all_scored_rails': scored_rails,
            'preference_applied': payment_data.get('routing_preference', 'balanced'),
            'scoring_method': f"Weighted: {selected['speed_weight']:.1%} speed, {selected['cost_weight']:.1%} cost",
            'justification': reason
        }
    
    def process_payment(self, payment_data: dict) -> dict:
        """Process payment with AI rail selection"""
        payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Determine available rails based on payment type
        # In real scenario, this would come from payment type config
        corridor = f"{payment_data['sender_country']}_{payment_data['receiver_country']}"
        corridor_data = MockDataSources.get_corridor(corridor)
        
        if not corridor_data:
            raise ValueError(f"Unsupported corridor: {corridor}")
        
        available_rails = corridor_data['available_rails']
        
        # AI selects optimal rail
        selection_result = self.select_optimal_rail(payment_data, available_rails)
        
        if not selection_result['selected']:
            raise ValueError("No suitable rails found for this payment")
        
        selected_rail = selection_result['selected']['rail']
        
        # Simulate processing
        processing_time = random.uniform(1.5, 4.5)
        
        # Store in state manager
        self.state_manager.record_payment(payment_id, {
            'amount': payment_data['amount'],
            'rail': selected_rail,
            'status': 'COMPLETED',
            'processing_time': processing_time
        })
        
        return {
            "payment_id": payment_id,
            "status": "COMPLETED",
            "selected_rail": selected_rail,
            "backup_rail": selection_result['runner_up']['rail'] if selection_result['runner_up'] else "NONE",
            "total_processing_time": processing_time,
            "actual_cost": selection_result['selected']['attributes']['cost_score'],
            "fraud_check_score": random.uniform(0.001, 0.150),
            "sanctions_check_status": "APPROVED",
            "validation_violations": [],
            "selection_details": selection_result,
            "message_conversion": {
                "original": "MT103",
                "converted": "MX/PACS.009",
                "conversion_time_ms": random.randint(50, 200)
            }
        }

class MockStateManager:
    """Enhanced state manager with payment tracking"""
    
    def __init__(self):
        self._payments = {}
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M')}"
        self.start_time = datetime.now()
        self.preference_counts = {"fastest": 0, "cheapest": 0, "balanced": 0}
        self.rail_usage = {}
        self.total_volume = 0.0
    
    def record_payment(self, payment_id: str, data: dict):
        self._payments[payment_id] = data
        self.total_volume += data['amount']
        
        # Track rail usage
        rail = data['rail']
        self.rail_usage[rail] = self.rail_usage.get(rail, 0) + 1
        
        # Track preference (would need to pass preference through)
        # Mock for now
        if random.random() > 0.5:
            self.preference_counts['fastest'] += 1
        else:
            self.preference_counts['cheapest'] += 1
    
    def get_session_summary(self) -> dict:
        total = len(self._payments)
        successful = sum(1 for p in self._payments.values() if p.get('status') == 'COMPLETED')
        avg_time = sum(p.get('processing_time', 0) for p in self._payments.values()) / total if total > 0 else 0
        
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_payments": total,
            "total_volume": self.total_volume,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful / total if total > 0 else 0.0),
            "avg_processing_time": round(avg_time, 3),
            "rails_used": self.rail_usage,
            "preference_analysis": self.preference_counts
        }
    
    def reset(self):
        self._payments.clear()
        self.start_time = datetime.now()
        self.preference_counts = {"fastest": 0, "cheapest": 0, "balanced": 0}
        self.rail_usage.clear()
        self.total_volume = 0.0

class MockLogCapture:
    def __init__(self):
        self.logs = {}
        self.global_buffer = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    def add_log(self, payment_id: str, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {level:7s} [{payment_id}] {message}"
        
        with self.lock:
            self.global_buffer.append(log_entry)
    
    def finalize(self, payment_id: str, status: str):
        self.add_log(payment_id, f"Final status: {status}", "INFO")
        self.add_log(payment_id, "=" * 80, "INFO")

# Global instances
orchestrator = MockPaymentOrchestrator()
log_capture = MockLogCapture()

# ============================================================
# FASTAPI SETUP
# ============================================================

app = FastAPI(
    title="Payment Orchestrator API (Enhanced)",
    description="AI-Powered Multi-Rail Payment Orchestration",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch ALL unhandled exceptions and return proper JSON"""
    error_msg = f"Server Error: {str(exc)}"
    logging.error(f"💥 CRASH: {error_msg}\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": error_msg,
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )
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
    routing_preference: str = Field(default="fastest", description="fastest/cheapest/balanced")
    urgency: int = Field(default=5, ge=1, le=10, description="1-10 scale")
    risk_tolerance: int = Field(default=7, ge=1, le=10, description="1-10 scale")

class PaymentResponse(BaseModel):
    """Complete response model matching orchestrator output"""
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
    logs: Optional[List[Dict]] = None
    
    # Enhanced multi-rail fields (Optional to avoid breaking)
    validation_violations: Optional[List[str]] = None
    validation_warnings: Optional[List[str]] = None
    fraud_check_score: Optional[float] = None
    sanctions_check_status: Optional[str] = None
    message_conversion: Optional[Dict] = None
    selection_details: Optional[Dict] = None
# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "payment-orchestrator-enhanced"
    }

@app.post("/api/v1/payment/process", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """Process payment with multi-rail AI selection"""
    
    # Generate payment ID
    payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())}"
    
    try:
        # Convert Pydantic model to dict (FIX for Pydantic v2)
        payment_data = payment.model_dump()  # ✅ FIX: use model_dump()
        payment_data["payment_id"] = payment_id
        
        # Log payment start
        log_capture.add_log(payment_id, "=" * 80, "INFO")
        log_capture.add_log(payment_id, f"NEW PAYMENT: {payment_id}", "INFO")
        log_capture.add_log(payment_id, f"Amount: {payment_data['amount']} {payment_data['currency_from']}", "INFO")
        log_capture.add_log(payment_id, f"Preference: {payment_data['routing_preference']}", "INFO")
        
        # Process through orchestrator
        result = orchestrator.process_payment(payment_data)
        
        # Ensure required fields exist for PaymentResponse
        result.setdefault("payment_id", payment_id)
        result.setdefault("state_key", f"STATE_{payment_id}")
        result.setdefault("status", "COMPLETED")
        result.setdefault("compliance_status", "APPROVED")
        result.setdefault("layer4_validation", "APPROVED")
        result.setdefault("selected_rail", result.get("selected_rail", "UNKNOWN"))
        result.setdefault("backup_rail", result.get("backup_rail", "UNKNOWN"))
        result.setdefault("risk_score", 0.0)
        result.setdefault("actual_cost", 0.0)
        result.setdefault("actual_processing_time", 0.0)
        result.setdefault("success", True)
        result.setdefault("total_processing_time", 0.0)
        result.setdefault("reconciliation_status", "PENDING")
        result.setdefault("logs", [])
        
        return result
        
    except Exception as e:
        # Log the crash
        error_details = traceback.format_exc()
        log_capture.add_log(payment_id, f"❌ FATAL ERROR: {str(e)}", "ERROR")
        log_capture.add_log(payment_id, f"Traceback: {error_details}", "ERROR")
        
        # Return structured error (will be caught by global handler)
        raise HTTPException(
            status_code=500,
            detail=f"Payment processing crashed: {str(e)}"
        )

@app.get("/api/v1/metrics/session")
async def get_session_metrics():
    return orchestrator.state_manager.get_session_summary()

@app.get("/api/v1/logs")
async def get_logs(last_n: int = 100):
    with log_capture.lock:
        logs = list(log_capture.global_buffer)[-last_n:]
    return {"logs": logs, "total_logs": len(log_capture.global_buffer)}

@app.post("/api/v1/logs/clear")
async def clear_logs():
    with log_capture.lock:
        log_capture.global_buffer.clear()
    return {"status": "success", "message": "Logs cleared"}

@app.post("/api/v1/metrics/reset")
async def reset_metrics():
    orchestrator.state_manager.reset()
    with log_capture.lock:
        log_capture.global_buffer.clear()
    return {"status": "success", "message": "Session reset"}

@app.get("/api/v1/rails")
async def get_rails():
    """Get all rails with performance data"""
    return {"rails": [
        {
            "rail": name,
            **data
        }
        for name, data in MockDataSources.RAILS.items()
    ]}

@app.get("/api/v1/corridors")
async def get_corridors():
    return {"corridors": [
        {"corridor": name, **data}
        for name, data in MockDataSources.CORRIDORS.items()
    ]}

# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  ENHANCED PAYMENT ORCHESTRATOR - MULTI-RAIL AI SELECTION")
    print("=" * 80)
    print("\n🤖 AI will intelligently select from multiple rails per payment type")
    print("📊 Enhanced scoring algorithm with preference weighting")
    print("📈 Real-time justification and decision transparency")
    print("\n📡 API URL: http://localhost:8000")
    print("\n" + "=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")