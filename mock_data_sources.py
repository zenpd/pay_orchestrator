"""
Mock Data Sources - Enhanced for Realistic Rail Selection Demos
Multiple rails per payment type with rich attributes for AI scoring
"""

import random
from typing import Dict, List, Any
from datetime import datetime

class MockDataSources:
    """Enhanced mock data with granular rail attributes"""
    
    # === ENHANCED RAIL PERFORMANCE METADATA ===
    # Each rail now has detailed attributes for AI scoring
    
    RAIL_PERFORMANCE = {
        # === SWIFT Options ===
        "SWIFT_GPI": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "CROSS_BORDER_EXPRESS",
            "success_rate": 0.982,
            "avg_processing_time_hours": 4.2,
            "avg_cost_usd": 28.50,
            "cost_breakdown": {"base_fee": 15.00, "correspondent_fee": 8.50, "fx_markup": 5.00},
            "availability": 0.997,
            "message_format": "MT→MX",
            "daily_volume_limit": 50000000,
            "eft_replacement_ready": True,
            "last_24h_volume": 4523,
            "last_24h_failures": 82,
            # NEW: Scoring attributes
            "speed_score": 95,  # 0-100
            "cost_score": 30,   # 0-100 (lower cost = higher score)
            "risk_level": "LOW",
            "regulatory_overhead": "HIGH",  # Compliance complexity
            "liquidity_requirement": "HIGH",  # Prefunding needed
            "supports_high_value": True,
            "target_use_case": ["Cross-Border", "Urgent", "High-Value"]
        },
        "SWIFT_TRADITIONAL": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "CROSS_BORDER_STANDARD",
            "success_rate": 0.945,
            "avg_processing_time_hours": 24.0,
            "avg_cost_usd": 22.00,
            "cost_breakdown": {"base_fee": 12.00, "correspondent_fee": 6.00, "fx_markup": 4.00},
            "availability": 0.985,
            "message_format": "MT→MX",
            "daily_volume_limit": 30000000,
            "eft_replacement_ready": True,
            "last_24h_volume": 1234,
            "last_24h_failures": 68,
            "speed_score": 60,
            "cost_score": 45,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "liquidity_requirement": "MEDIUM",
            "supports_high_value": True,
            "target_use_case": ["Cross-Border", "Standard", "Cost-Focused"]
        },
        
        # === PayShap Options ===
        "PayShap_INSTANT": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.995,
            "avg_processing_time_hours": 0.001,  # 3.6 seconds
            "avg_cost_usd": 0.25,
            "cost_breakdown": {"base_fee": 0.15, "network_fee": 0.10},
            "availability": 0.999,
            "message_format": "MX",
            "daily_volume_limit": 500000,
            "eft_replacement_ready": True,
            "last_24h_volume": 8945,
            "last_24h_failures": 45,
            "speed_score": 100,
            "cost_score": 95,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "liquidity_requirement": "NONE",
            "supports_high_value": False,  # Max R50,000
            "target_use_case": ["Domestic", "Instant", "Low-Value", "Retail"]
        },
        "PayShap_SCHEDULED": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "DOMESTIC_BATCHED",
            "success_rate": 0.99,
            "avg_processing_time_hours": 4.0,
            "avg_cost_usd": 0.15,
            "cost_breakdown": {"base_fee": 0.10, "batch_fee": 0.05},
            "availability": 0.998,
            "message_format": "MX",
            "daily_volume_limit": 1000000,
            "eft_replacement_ready": True,
            "last_24h_volume": 12345,
            "last_24h_failures": 123,
            "speed_score": 70,  # Slower due to batching
            "cost_score": 98,   # Cheapest
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "liquidity_requirement": "NONE",
            "supports_high_value": False,
            "target_use_case": ["Domestic", "Scheduled", "Bulk", "Cost-Focused"]
        },
        
        # === RTGS Options ===
        "RTGS_HIGH_VALUE": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "DOMESTIC_HIGH_VALUE",
            "success_rate": 0.999,
            "avg_processing_time_hours": 1.0,
            "avg_cost_usd": 25.00,
            "cost_breakdown": {"base_fee": 20.00, "priority_fee": 5.00},
            "availability": 0.999,
            "message_format": "MX",
            "daily_volume_limit": 5000000,
            "eft_replacement_ready": False,  # Already modern
            "last_24h_volume": 567,
            "last_24h_failures": 2,
            "speed_score": 85,
            "cost_score": 25,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "MEDIUM",
            "liquidity_requirement": "HIGH",
            "supports_high_value": True,  # Unlimited
            "target_use_case": ["Domestic", "High-Value", "Priority", "Corporate"]
        },
        "RTGS_BULK": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "DOMESTIC_BULK_BATCH",
            "success_rate": 0.98,
            "avg_processing_time_hours": 6.0,  # End-of-day
            "avg_cost_usd": 0.50,
            "cost_breakdown": {"base_fee": 0.30, "batch_fee": 0.20},
            "availability": 0.995,
            "message_format": "MX",
            "daily_volume_limit": 50000000,
            "eft_replacement_ready": False,
            "last_24h_volume": 45678,
            "last_24h_failures": 913,
            "speed_score": 50,  # Slow due to EOD batch
            "cost_score": 90,   # Very cheap per item
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "liquidity_requirement": "NONE",
            "supports_high_value": True,  # For bulk payroll
            "target_use_case": ["Domestic", "Bulk", "Payroll", "Cost-Focused"]
        },
        
        # === Partner Rails (Future-proofing) ===
        "CIPS": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "CROSS_BORDER_CIPS",
            "success_rate": 0.94,
            "avg_processing_time_hours": 4.0,
            "avg_cost_usd": 15.00,
            "cost_breakdown": {"base_fee": 10.00, "cips_fee": 5.00},
            "availability": 0.96,
            "message_format": "MX",
            "daily_volume_limit": 200000,
            "eft_replacement_ready": False,
            "last_24h_volume": 345,
            "last_24h_failures": 21,
            "speed_score": 88,
            "cost_score": 50,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "liquidity_requirement": "MEDIUM",
            "supports_high_value": True,
            "target_use_case": ["Cross-Border", "CNY", "Alternative", "Mid-Cost"]
        },
        "Remitly": {
            "speed_score": 85,              # 0-100 (higher = faster)
            "cost_score": 60,               # 0-100 (higher = cheaper)
            "risk_level": "LOW",            # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
            "regulatory_overhead": "MEDIUM", # "LOW", "MEDIUM", "HIGH"
            "supports_high_value": True,    # bool
            "capacity_per_hour": 1000,      # transactions per hour
            "max_amount": 10000000,         # maximum transaction amount
            "type": "CROSS_BORDER_REMITTANCE",
            "success_rate": 0.92,
            "avg_processing_time_hours": 0.5,
            "avg_cost_usd": 3.99,
            "cost_breakdown": {"base_fee": 2.99, "fx_markup": 1.00},
            "availability": 0.97,
            "message_format": "CUSTOM",
            "daily_volume_limit": 50000,
            "eft_replacement_ready": False,
            "last_24h_volume": 789,
            "last_24h_failures": 63,
            "speed_score": 92,
            "cost_score": 85,  # Low cost for small amounts
            "risk_level": "MEDIUM",
            "regulatory_overhead": "HIGH",  # Partner due diligence
            "liquidity_requirement": "NONE",
            "supports_high_value": False,  # Max $10,000
            "target_use_case": ["Cross-Border", "Remittance", "Low-Value", "Consumer"]
        }
    }
    
    # === PRE-VALIDATION RULES (Left-Shifted) ===
    PRE_VALIDATION_RULES = {
        "business_rules": {
            "amount_check": {"enabled": True, "max_amount": 10000000, "min_amount": 0.01},
            "holiday_check": {"enabled": True, "blocked_dates": ["2025-12-25", "2026-01-01"]},
            "cutoff_check": {"enabled": True, "cutoff_time": "16:00"},
            "future_date_validation": {"enabled": True, "max_future_days": 30},
            "duplicate_check": {"enabled": True, "lookback_hours": 24},
            "charges_fees_update": {"enabled": True},
            "limit_check": {"enabled": True, "daily_limit": 1000000},
            "balance_check": {"enabled": True},
            "purpose_code_check": {"enabled": True, "valid_codes": ["TRADE", "PAYROLL", "SUPPLY", "INVESTMENT", "LOAN"]}
        },
        "payment_rail_validations": {
            "duplicate_check": {"enabled": True},
            "sanctions_check": {"enabled": True, "check_level": "ENHANCED"},
            "fraud_check": {"enabled": True, "ml_model_version": "v2.1"},
            "charges_fees_integration": {"enabled": True}
        }
    }
    
    # === CORRIDORS WITH MULTIPLE RAIL OPTIONS ===
    CORRIDORS = {
        "ZA_ZA": {
            "available_rails": [
                "PayShap_INSTANT", "PayShap_SCHEDULED", 
                "RTGS_HIGH_VALUE", "RTGS_BULK"
            ],
            "default_rail": "PayShap_INSTANT",
            "eft_replacement_rail": "PayShap_INSTANT",
            "compliance_level": "MEDIUM",
            "avg_processing_hours": 2.0,
            "daily_volume_limit": 100000000,
            "regulatory_requirements": ["FICA", "PASA"],
            "business_hours": "07:00-18:00",
            "cut_off_time": "15:30"
        },
        "ZA_US": {
            "available_rails": [
                "SWIFT_GPI", "SWIFT_TRADITIONAL", "CIPS"
            ],
            "default_rail": "SWIFT_GPI",
            "eft_replacement_rail": None,
            "compliance_level": "HIGH",
            "avg_processing_hours": 4.5,
            "daily_volume_limit": 50000000,
            "regulatory_requirements": ["FICA", "SARB_APPROVAL", "FinCEN"],
            "business_hours": "24/7",
            "cut_off_time": None
        },
        "ZA_GB": {
            "available_rails": [
                "SWIFT_GPI", "SWIFT_TRADITIONAL", "CIPS"
            ],
            "default_rail": "SWIFT_GPI",
            "eft_replacement_rail": None,
            "compliance_level": "HIGH",
            "avg_processing_hours": 3.2,
            "daily_volume_limit": 40000000,
            "regulatory_requirements": ["FICA", "SARB_APPROVAL", "FCA"],
            "business_hours": "24/7",
            "cut_off_time": None
        },
        "ZA_BW": {
            "available_rails": [
                "SADC_PAY", "SWIFT_GPI", "SWIFT_TRADITIONAL"
            ],
            "default_rail": "SADC_PAY",
            "eft_replacement_rail": "SADC_PAY",
            "compliance_level": "MEDIUM",
            "avg_processing_hours": 2.5,
            "daily_volume_limit": 30000000,
            "regulatory_requirements": ["FICA", "SARB_APPROVAL", "BoB"],
            "business_hours": "24/7",
            "cut_off_time": None
        }
    }
    
    # === PAYMENT TYPE TO RAIL MAPPING (For Demo Scenarios) ===
    PAYMENT_TYPE_SCENARIOS = {
        "Cross-Border Payment": {
            "corridor": "ZA_US",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "CIPS"],
            "default_preference": "fastest",
            "amount_range": (50000, 500000),
            "purpose_codes": ["TRADE", "INVESTMENT"]
        },
        "Domestic Bulk Payment": {
            "corridor": "ZA_ZA",
            "rails": ["RTGS_BULK", "PayShap_SCHEDULED"],
            "default_preference": "cheapest",
            "amount_range": (500000, 5000000),
            "purpose_codes": ["PAYROLL", "SUPPLY"]
        },
        "Domestic Non-Bulk (Instant)": {
            "corridor": "ZA_ZA",
            "rails": ["PayShap_INSTANT", "RTGS_HIGH_VALUE"],
            "default_preference": "fastest",
            "amount_range": (5000, 50000),
            "purpose_codes": ["LOAN", "SALARY"]
        },
        "Domestic Non-Bulk (Scheduled)": {
            "corridor": "ZA_ZA",
            "rails": ["PayShap_SCHEDULED", "RTGS_BULK"],
            "default_preference": "cheapest",
            "amount_range": (15000, 100000),
            "purpose_codes": ["SUPPLY", "TRADE"]
        },
        "SADC Regional Payment": {
            "corridor": "ZA_BW",
            "rails": ["SADC_PAY", "SWIFT_GPI"],
            "default_preference": "fastest",
            "amount_range": (35000, 200000),
            "purpose_codes": ["TRADE", "INVESTMENT"]
        }
    }
    
    @classmethod
    def get_validation_rules(cls) -> Dict:
        """Return left-shifted pre-validation rules"""
        return cls.PRE_VALIDATION_RULES
    
    @classmethod
    def get_fx_rate(cls, currency_pair: str) -> Dict:
        """Get FX rate with realistic spread"""
        if currency_pair not in cls.FX_RATES:
            return {"rate": 1.0, "spread": 0.0, "last_update": datetime.now().isoformat()}
        
        base_rate = cls.FX_RATES[currency_pair]
        rate = base_rate["rate"] + random.uniform(-base_rate["spread"], base_rate["spread"])
        
        return {
            "rate": round(rate, 6),
            "spread": base_rate["spread"],
            "bid": round(rate - base_rate["spread"]/2, 6),
            "ask": round(rate + base_rate["spread"]/2, 6),
            "last_update": datetime.now().isoformat(),
            "source": "Reuters Market Data Feed"
        }
    
    @classmethod
    def get_corridor_metadata(cls, corridor: str) -> Dict:
        """Get corridor configuration from PoC scope"""
        return cls.CORRIDORS.get(corridor, {
            "available_rails": ["SWIFT_GPI"],
            "default_rail": "SWIFT_GPI",
            "eft_replacement_rail": None,
            "compliance_level": "HIGH",
            "avg_processing_hours": 24.0,
            "daily_volume_limit": 10000000,
            "regulatory_requirements": ["STANDARD"]
        })