"""
Rail and corridor constants for pay_orchestrator.
"""
from __future__ import annotations
from typing import Final

# ── Payment Rails ─────────────────────────────────────────────────────────────
RAIL_PERFORMANCE: Final[dict] = {
    "SWIFT_GPI": {
        "speed_score": 95,
        "cost_score": 30,
        "risk_level": "LOW",
        "regulatory_overhead": "HIGH",
        "max_amount": 10_000_000,
        "avg_cost_usd": 28.50,
        "success_rate": 0.982,
        "availability": 0.995,
        "avg_processing_hours": 4,
        "current_load": "NORMAL",
        "supports_high_value": True,
        "eft_replacement_ready": True,
    },
    "SWIFT_TRADITIONAL": {
        "speed_score": 60,
        "cost_score": 45,
        "risk_level": "MEDIUM",
        "regulatory_overhead": "HIGH",
        "max_amount": 10_000_000,
        "avg_cost_usd": 22.00,
        "success_rate": 0.965,
        "availability": 0.990,
        "avg_processing_hours": 24,
        "current_load": "NORMAL",
        "supports_high_value": True,
        "eft_replacement_ready": True,
    },
    "PayShap_INSTANT": {
        "speed_score": 100,
        "cost_score": 95,
        "risk_level": "LOW",
        "regulatory_overhead": "LOW",
        "max_amount": 500_000,
        "avg_cost_usd": 0.25,
        "success_rate": 0.994,
        "availability": 0.998,
        "avg_processing_hours": 0.017,  # ~1 minute
        "current_load": "NORMAL",
        "supports_high_value": False,
        "eft_replacement_ready": True,
    },
    "PayShap_SCHEDULED": {
        "speed_score": 70,
        "cost_score": 98,
        "risk_level": "LOW",
        "regulatory_overhead": "LOW",
        "max_amount": 1_000_000,
        "avg_cost_usd": 0.15,
        "success_rate": 0.991,
        "availability": 0.997,
        "avg_processing_hours": 2,
        "current_load": "NORMAL",
        "supports_high_value": False,
        "eft_replacement_ready": True,
    },
    "RTGS_HIGH_VALUE": {
        "speed_score": 85,
        "cost_score": 25,
        "risk_level": "VERY_LOW",
        "regulatory_overhead": "MEDIUM",
        "max_amount": 5_000_000,
        "avg_cost_usd": 25.00,
        "success_rate": 0.997,
        "availability": 0.995,
        "avg_processing_hours": 1,
        "current_load": "NORMAL",
        "supports_high_value": True,
        "eft_replacement_ready": False,
    },
    "RTGS_BULK": {
        "speed_score": 50,
        "cost_score": 90,
        "risk_level": "LOW",
        "regulatory_overhead": "LOW",
        "max_amount": 2_000_000,
        "avg_cost_usd": 0.50,
        "success_rate": 0.989,
        "availability": 0.993,
        "avg_processing_hours": 24,
        "current_load": "NORMAL",
        "supports_high_value": False,
        "eft_replacement_ready": False,
    },
    "SADC_PAY": {
        "speed_score": 78,
        "cost_score": 80,
        "risk_level": "MEDIUM",
        "regulatory_overhead": "MEDIUM",
        "max_amount": 1_000_000,
        "avg_cost_usd": 5.00,
        "success_rate": 0.970,
        "availability": 0.985,
        "avg_processing_hours": 4,
        "current_load": "NORMAL",
        "supports_high_value": False,
        "eft_replacement_ready": True,
    },
    "CORRESPONDENT": {
        "speed_score": 40,
        "cost_score": 20,
        "risk_level": "MEDIUM",
        "regulatory_overhead": "HIGH",
        "max_amount": 10_000_000,
        "avg_cost_usd": 35.00,
        "success_rate": 0.940,
        "availability": 0.980,
        "avg_processing_hours": 48,
        "current_load": "HIGH",
        "supports_high_value": True,
        "eft_replacement_ready": False,
    },
}

# ── Corridors ─────────────────────────────────────────────────────────────────
CORRIDORS: Final[dict] = {
    "ZA_ZA": {
        "available_rails": ["PayShap_INSTANT", "PayShap_SCHEDULED", "RTGS_HIGH_VALUE", "RTGS_BULK"],
        "default_rail": "PayShap_INSTANT",
        "compliance_level": "LOW",
        "regulatory_requirements": ["FICA"],
        "eft_replacement": "PayShap_INSTANT",
    },
    "ZA_US": {
        "available_rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "CORRESPONDENT"],
        "default_rail": "SWIFT_GPI",
        "compliance_level": "HIGH",
        "regulatory_requirements": ["FICA", "SARB_APPROVAL", "FinCEN"],
        "eft_replacement": None,
    },
    "ZA_GB": {
        "available_rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "CORRESPONDENT"],
        "default_rail": "SWIFT_GPI",
        "compliance_level": "HIGH",
        "regulatory_requirements": ["FICA", "SARB_APPROVAL"],
        "eft_replacement": None,
    },
    "ZA_BW": {
        "available_rails": ["SADC_PAY", "SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "default_rail": "SADC_PAY",
        "compliance_level": "MEDIUM",
        "regulatory_requirements": ["FICA", "SARB_APPROVAL"],
        "eft_replacement": "SADC_PAY",
    },
    "ZA_ZW": {
        "available_rails": ["SADC_PAY", "SWIFT_GPI"],
        "default_rail": "SADC_PAY",
        "compliance_level": "HIGH",
        "regulatory_requirements": ["FICA", "SARB_APPROVAL", "OFAC_CHECK"],
        "eft_replacement": None,
    },
}

# ── FX Rates (mock — replaced by live feed in production) ────────────────────
FX_RATES: Final[dict] = {
    "ZAR_USD": 0.054,
    "ZAR_EUR": 0.049,
    "ZAR_GBP": 0.042,
    "USD_ZAR": 18.52,
    "EUR_ZAR": 20.41,
    "GBP_ZAR": 23.81,
    "USD_EUR": 0.91,
    "EUR_USD": 1.10,
    "USD_GBP": 0.78,
    "GBP_USD": 1.28,
    "ZAR_BWP": 0.077,
    "BWP_ZAR": 12.97,
    "ZAR_ZWL": 3.50,
    "ZWL_ZAR": 0.286,
}

# ── Pre-validation Rules ──────────────────────────────────────────────────────
PRE_VALIDATION_RULES: Final[dict] = {
    "business_rules": [
        {"id": "BIZ-001", "name": "amount_check", "description": "Payment amount must be positive and within global limit"},
        {"id": "BIZ-002", "name": "holiday_check", "description": "Payment cannot be submitted on bank holidays"},
        {"id": "BIZ-003", "name": "cutoff_check", "description": "Payment must be submitted before cut-off time"},
        {"id": "BIZ-004", "name": "future_date", "description": "Value date cannot be more than 30 days in future"},
        {"id": "BIZ-005", "name": "duplicate_check", "description": "Duplicate payment detection within 24h"},
        {"id": "BIZ-006", "name": "charges_fees", "description": "Sender must have sufficient balance including fees"},
        {"id": "BIZ-007", "name": "corridor_limit", "description": "Amount must be within corridor-specific limit"},
        {"id": "BIZ-008", "name": "balance_check", "description": "Sender account must have sufficient balance"},
        {"id": "BIZ-009", "name": "purpose_code", "description": "Payment purpose code is required for this corridor"},
    ],
    "payment_rail_validations": [
        {"id": "RAIL-001", "name": "duplicate_rail", "description": "No duplicate transaction on same rail within 5 minutes"},
        {"id": "RAIL-002", "name": "sanctions_screen", "description": "Sender/receiver must pass OFAC/UN/EU sanctions screening"},
        {"id": "RAIL-003", "name": "fraud_score", "description": "ML fraud score must be below 0.75 threshold"},
        {"id": "RAIL-004", "name": "charges_fees_rail", "description": "Rail-specific fee must be covered by sender balance"},
    ],
}

# ── Risk Thresholds ───────────────────────────────────────────────────────────
RISK_SCORE_REJECT: Final[float] = 0.80
RISK_SCORE_HOLD: Final[float] = 0.50

# ── High-risk countries (FATF grey/black list) ────────────────────────────────
HIGH_RISK_COUNTRIES: Final[frozenset] = frozenset(
    ["AF", "KP", "IR", "MM", "SY", "CU", "YE", "SO", "SS", "VE", "PK"]
)

# ── Payment scenarios for demos ───────────────────────────────────────────────
PAYMENT_TYPE_SCENARIOS: Final[dict] = {
    "domestic_instant": {
        "corridor": "ZA_ZA",
        "preferred_rails": ["PayShap_INSTANT"],
        "routing_preference": "fastest",
        "amount_range": (100, 50_000),
        "purpose_codes": ["SALA", "GDDS", "SUPP"],
    },
    "cross_border_high_value": {
        "corridor": "ZA_US",
        "preferred_rails": ["SWIFT_GPI"],
        "routing_preference": "balanced",
        "amount_range": (10_000, 250_000),
        "purpose_codes": ["TRAD", "INVS", "SVCS"],
    },
    "sadc_regional": {
        "corridor": "ZA_BW",
        "preferred_rails": ["SADC_PAY"],
        "routing_preference": "cheapest",
        "amount_range": (500, 20_000),
        "purpose_codes": ["GDDS", "SVCS"],
    },
}
