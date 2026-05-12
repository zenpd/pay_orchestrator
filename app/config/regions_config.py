"""
Regional Configuration - Multi-Region Support
Defines payment rails, currencies, corridors for each region
"""

# ============================================================
# SOUTH AFRICA REGION
# ============================================================
SOUTH_AFRICA_REGION = {
    "name": "South Africa",
    "code": "ZA",
    "domestic_currency": "ZAR",
    "region_type": "SADC",
    "payment_types": {
        "Cross-Border Payment": {
            "description": "International payments with MT→MX conversion",
            "corridor": "ZA_US",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "NAMPAY"],
            "default_currency": ("ZAR", "USD"),
            "example_amount": 50000.0,
            "typical_use": "High-value international transfers"
        },
        "Domestic Bulk Payment": {
            "description": "High-volume batch payments (EOD processing)",
            "corridor": "ZA_ZA",
            "rails": ["RTGS_BULK", "BATCH_ACH", "SLOW_BATCH"],
            "default_currency": ("ZAR", "ZAR"),
            "example_amount": 500000.0,
            "typical_use": "Payroll, supplier bulk payments"
        },
        "Domestic Instant": {
            "description": "Real-time small-value payments",
            "corridor": "ZA_ZA",
            "rails": ["PayShap_INSTANT", "RTGS_REALTIME"],
            "default_currency": ("ZAR", "ZAR"),
            "example_amount": 5000.0,
            "typical_use": "P2P, urgent payments"
        },
        "Domestic Scheduled": {
            "description": "Scheduled domestic payments (4-hour batches)",
            "corridor": "ZA_ZA",
            "rails": ["PayShap_SCHEDULED", "STANDING_ORDER"],
            "default_currency": ("ZAR", "ZAR"),
            "example_amount": 15000.0,
            "typical_use": "Recurring bills, scheduled transfers"
        },
        "SADC Regional": {
            "description": "SADC corridor payments with regional compliance",
            "corridor": "ZA_BW",
            "rails": ["SADC_PAY", "SWIFT_GPI", "REGIONAL_PARTNER"],
            "default_currency": ("ZAR", "USD"),
            "example_amount": 35000.0,
            "typical_use": "Regional trade, cross-border"
        }
    },
    "rails": {
        "SWIFT_GPI": {
            "type": "CROSS_BORDER_EXPRESS",
            "success_rate": 0.98,
            "avg_cost_usd": 28.50,
            "speed_score": 95,
            "cost_score": 30,
            "max_amount": 10000000,
            "risk_level": "LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500,
            "availability": 0.995,
            "processing_time": "4.2 hours",
            "supported_corridors": ["ZA_US", "ZA_GB"]
        },
        "SWIFT_TRADITIONAL": {
            "type": "CROSS_BORDER_STANDARD",
            "success_rate": 0.945,
            "avg_cost_usd": 22.00,
            "speed_score": 60,
            "cost_score": 45,
            "max_amount": 10000000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 500,
            "availability": 0.985,
            "processing_time": "24 hours",
            "supported_corridors": ["ZA_US", "ZA_GB"]
        },
        "PayShap_INSTANT": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.995,
            "avg_cost_usd": 0.25,
            "speed_score": 100,
            "cost_score": 95,
            "max_amount": 50000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 5000,
            "availability": 0.999,
            "processing_time": "3.6 seconds"
        },
        "PayShap_SCHEDULED": {
            "type": "DOMESTIC_BATCHED",
            "success_rate": 0.99,
            "avg_cost_usd": 0.15,
            "speed_score": 70,
            "cost_score": 98,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 10000,
            "availability": 0.998,
            "processing_time": "4 hours"
        },
        "RTGS_BULK": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.999,
            "avg_cost_usd": 25.00,
            "speed_score": 85,
            "cost_score": 40,
            "max_amount": 5000000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 1000,
            "availability": 0.999,
            "processing_time": "1 hour"
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
            "availability": 0.97
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
            "availability": 0.96
        },
        "BATCH_ACH": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.96,
            "avg_cost_usd": 0.20,
            "speed_score": 40,
            "cost_score": 98,
            "max_amount": 500000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 50000,
            "availability": 0.98
        }
    },
    "corridors": {
        "ZA_US": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "NAMPAY"],
        "ZA_GB": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "ZA_ZA": ["PayShap_INSTANT", "PayShap_SCHEDULED", "RTGS_BULK", "BATCH_ACH"],
        "ZA_BW": ["SADC_PAY"],
        "ZA_ZW": ["SADC_PAY"],
        "ZA_MZ": ["SADC_PAY"]
    }
}

# ============================================================
# UNITED STATES REGION
# ============================================================
UNITED_STATES_REGION = {
    "name": "United States",
    "code": "US",
    "domestic_currency": "USD",
    "region_type": "NORTH_AMERICA",
    "payment_types": {
        "Domestic Wire Transfer": {
            "description": "Fast same-day wire transfers",
            "corridor": "US_US",
            "rails": ["FedWire", "ACH_Express", "RTP"],
            "default_currency": ("USD", "USD"),
            "example_amount": 25000.0,
            "typical_use": "Urgent domestic transfers"
        },
        "Domestic ACH (Bulk)": {
            "description": "Cost-effective bulk transfers (2-3 days)",
            "corridor": "US_US",
            "rails": ["ACH_Standard", "ACH_Batch"],
            "default_currency": ("USD", "USD"),
            "example_amount": 100000.0,
            "typical_use": "Payroll, batch payments"
        },
        "Domestic Real-Time Payment": {
            "description": "Instant money movement (RTP)",
            "corridor": "US_US",
            "rails": ["RTP", "CHIPS"],
            "default_currency": ("USD", "USD"),
            "example_amount": 50000.0,
            "typical_use": "Urgent, real-time transfers"
        },
        "International Wire": {
            "description": "Outbound international transfers",
            "corridor": "US_GB",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "INTERNATIONAL_ACH"],
            "default_currency": ("USD", "GBP"),
            "example_amount": 75000.0,
            "typical_use": "International payments, cross-border"
        },
        "Inbound International": {
            "description": "Incoming international transfers",
            "corridor": "GB_US",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
            "default_currency": ("GBP", "USD"),
            "example_amount": 50000.0,
            "typical_use": "Receive international payments"
        }
    },
    "rails": {
        "FedWire": {
            "type": "DOMESTIC_EXPRESS",
            "success_rate": 0.998,
            "avg_cost_usd": 15.00,
            "speed_score": 100,
            "cost_score": 50,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 1000,
            "availability": 0.9999,
            "processing_time": "30 minutes",
            "supported_corridors": ["US_US"]
        },
        "ACH_Express": {
            "type": "DOMESTIC_FAST",
            "success_rate": 0.995,
            "avg_cost_usd": 1.50,
            "speed_score": 90,
            "cost_score": 85,
            "max_amount": 25000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 10000,
            "availability": 0.998,
            "processing_time": "Same day"
        },
        "RTP": {
            "type": "DOMESTIC_REAL_TIME",
            "success_rate": 0.992,
            "avg_cost_usd": 0.50,
            "speed_score": 100,
            "cost_score": 90,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 50000,
            "availability": 0.997,
            "processing_time": "Instant"
        },
        "ACH_Standard": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.998,
            "avg_cost_usd": 0.25,
            "speed_score": 30,
            "cost_score": 98,
            "max_amount": 1000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 100000,
            "availability": 0.999,
            "processing_time": "2-3 days"
        },
        "SWIFT_GPI": {
            "type": "CROSS_BORDER_EXPRESS",
            "success_rate": 0.98,
            "avg_cost_usd": 30.00,
            "speed_score": 95,
            "cost_score": 35,
            "max_amount": 999999999,
            "risk_level": "LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500,
            "availability": 0.995,
            "processing_time": "2-4 hours"
        },
        "CHIPS": {
            "type": "DOMESTIC_HIGH_VALUE",
            "success_rate": 0.9999,
            "avg_cost_usd": 20.00,
            "speed_score": 95,
            "cost_score": 45,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "VERY_HIGH",
            "capacity_per_hour": 100,
            "availability": 0.9999,
            "processing_time": "Same day"
        },
        "ACH_Batch": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.997,
            "avg_cost_usd": 0.10,
            "speed_score": 20,
            "cost_score": 99,
            "max_amount": 500000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 500000,
            "availability": 0.998,
            "processing_time": "3-5 days"
        },
        "INTERNATIONAL_ACH": {
            "type": "CROSS_BORDER",
            "success_rate": 0.95,
            "avg_cost_usd": 12.00,
            "speed_score": 60,
            "cost_score": 80,
            "max_amount": 100000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 1000,
            "availability": 0.96
        }
    },
    "corridors": {
        "US_US": ["FedWire", "ACH_Express", "RTP", "ACH_Standard", "ACH_Batch", "CHIPS"],
        "US_GB": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "INTERNATIONAL_ACH"],
        "US_EU": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "GB_US": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "EU_US": ["SWIFT_GPI", "SWIFT_TRADITIONAL"]
    }
}

# ============================================================
# UNITED KINGDOM REGION
# ============================================================
UNITED_KINGDOM_REGION = {
    "name": "United Kingdom",
    "code": "GB",
    "domestic_currency": "GBP",
    "region_type": "EUROPE",
    "payment_types": {
        "Faster Payment": {
            "description": "Faster Payments Service (same day)",
            "corridor": "GB_GB",
            "rails": ["FPS", "BACS_Express"],
            "default_currency": ("GBP", "GBP"),
            "example_amount": 30000.0,
            "typical_use": "Same-day domestic payments"
        },
        "BACS Transfer": {
            "description": "BACS bulk payments (3-5 days)",
            "corridor": "GB_GB",
            "rails": ["BACS", "BACS_Batch"],
            "default_currency": ("GBP", "GBP"),
            "example_amount": 150000.0,
            "typical_use": "Payroll, bulk transfers"
        },
        "Real-Time Payment": {
            "description": "Faster Payments instant transfers",
            "corridor": "GB_GB",
            "rails": ["FPS_INSTANT", "CHAPS"],
            "default_currency": ("GBP", "GBP"),
            "example_amount": 100000.0,
            "typical_use": "Urgent, high-value transfers"
        },
        "Outbound International": {
            "description": "International transfers from UK",
            "corridor": "GB_US",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "UK_INTERNATIONAL"],
            "default_currency": ("GBP", "USD"),
            "example_amount": 50000.0,
            "typical_use": "International payments"
        },
        "Inbound International": {
            "description": "Receive international transfers",
            "corridor": "US_GB",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
            "default_currency": ("USD", "GBP"),
            "example_amount": 75000.0,
            "typical_use": "Receive from abroad"
        }
    },
    "rails": {
        "FPS": {
            "type": "DOMESTIC_FAST",
            "success_rate": 0.998,
            "avg_cost_usd": 2.50,
            "speed_score": 95,
            "cost_score": 85,
            "max_amount": 250000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 100000,
            "availability": 0.998,
            "processing_time": "30 minutes",
            "supported_corridors": ["GB_GB"]
        },
        "BACS": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.999,
            "avg_cost_usd": 0.15,
            "speed_score": 40,
            "cost_score": 98,
            "max_amount": 1000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 500000,
            "availability": 0.9999,
            "processing_time": "3-5 days"
        },
        "CHAPS": {
            "type": "DOMESTIC_HIGH_VALUE",
            "success_rate": 0.9999,
            "avg_cost_usd": 12.00,
            "speed_score": 100,
            "cost_score": 60,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 1000,
            "availability": 0.9999,
            "processing_time": "Same day"
        },
        "FPS_INSTANT": {
            "type": "DOMESTIC_REAL_TIME",
            "success_rate": 0.996,
            "avg_cost_usd": 1.00,
            "speed_score": 100,
            "cost_score": 88,
            "max_amount": 500000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 100000,
            "availability": 0.997,
            "processing_time": "Instant"
        },
        "SWIFT_GPI": {
            "type": "CROSS_BORDER_EXPRESS",
            "success_rate": 0.98,
            "avg_cost_usd": 28.00,
            "speed_score": 95,
            "cost_score": 35,
            "max_amount": 999999999,
            "risk_level": "LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500,
            "availability": 0.995,
            "processing_time": "2-4 hours"
        },
        "BACS_Express": {
            "type": "DOMESTIC_FAST",
            "success_rate": 0.997,
            "avg_cost_usd": 1.50,
            "speed_score": 85,
            "cost_score": 87,
            "max_amount": 500000,
            "risk_level": "LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 50000,
            "availability": 0.996,
            "processing_time": "1-2 days"
        },
        "BACS_Batch": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.998,
            "avg_cost_usd": 0.10,
            "speed_score": 30,
            "cost_score": 99,
            "max_amount": 1000000,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 1000000,
            "availability": 0.9999,
            "processing_time": "3-5 days"
        },
        "UK_INTERNATIONAL": {
            "type": "CROSS_BORDER",
            "success_rate": 0.96,
            "avg_cost_usd": 15.00,
            "speed_score": 70,
            "cost_score": 75,
            "max_amount": 500000,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 2000,
            "availability": 0.97
        }
    },
    "corridors": {
        "GB_GB": ["FPS", "BACS", "CHAPS", "FPS_INSTANT", "BACS_Express", "BACS_Batch"],
        "GB_US": ["SWIFT_GPI", "SWIFT_TRADITIONAL", "UK_INTERNATIONAL"],
        "GB_EU": ["SEPA", "SWIFT_GPI"],
        "US_GB": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "EU_GB": ["SEPA", "SWIFT_GPI"]
    }
}

# ============================================================
# EUROPE REGION (SEPA)
# ============================================================
EUROPE_REGION = {
    "name": "Europe",
    "code": "EU",
    "domestic_currency": "EUR",
    "region_type": "EUROPE",
    "payment_types": {
        "SEPA Transfer": {
            "description": "Single Euro Payment Area (1-2 days)",
            "corridor": "EU_EU",
            "rails": ["SEPA_CT", "SEPA_Batch"],
            "default_currency": ("EUR", "EUR"),
            "example_amount": 40000.0,
            "typical_use": "EU domestic transfers"
        },
        "SEPA Instant": {
            "description": "SEPA Instant Credit Transfer (10 seconds)",
            "corridor": "EU_EU",
            "rails": ["SEPA_INST", "TARGET2"],
            "default_currency": ("EUR", "EUR"),
            "example_amount": 100000.0,
            "typical_use": "Urgent EU transfers"
        },
        "SEPA Bulk": {
            "description": "SEPA batch processing",
            "corridor": "EU_EU",
            "rails": ["SEPA_Batch", "SEPA_Direct_Debit"],
            "default_currency": ("EUR", "EUR"),
            "example_amount": 500000.0,
            "typical_use": "Payroll, bulk payments"
        },
        "Outbound International": {
            "description": "Non-EU international transfers",
            "corridor": "EU_US",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
            "default_currency": ("EUR", "USD"),
            "example_amount": 75000.0,
            "typical_use": "Payments to US, outside EU"
        },
        "Inbound International": {
            "description": "Receive from non-EU countries",
            "corridor": "US_EU",
            "rails": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
            "default_currency": ("USD", "EUR"),
            "example_amount": 50000.0,
            "typical_use": "Receive from abroad"
        }
    },
    "rails": {
        "SEPA_CT": {
            "type": "DOMESTIC_STANDARD",
            "success_rate": 0.999,
            "avg_cost_usd": 1.50,
            "speed_score": 70,
            "cost_score": 92,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 100000,
            "availability": 0.9999,
            "processing_time": "1-2 days",
            "supported_corridors": ["EU_EU"]
        },
        "SEPA_INST": {
            "type": "DOMESTIC_INSTANT",
            "success_rate": 0.998,
            "avg_cost_usd": 2.50,
            "speed_score": 100,
            "cost_score": 85,
            "max_amount": 100000,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 50000,
            "availability": 0.998,
            "processing_time": "10 seconds"
        },
        "TARGET2": {
            "type": "DOMESTIC_HIGH_VALUE",
            "success_rate": 0.9999,
            "avg_cost_usd": 20.00,
            "speed_score": 100,
            "cost_score": 50,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "VERY_HIGH",
            "capacity_per_hour": 5000,
            "availability": 0.9999,
            "processing_time": "Real-time"
        },
        "SEPA_Batch": {
            "type": "DOMESTIC_BATCH",
            "success_rate": 0.9999,
            "avg_cost_usd": 0.20,
            "speed_score": 50,
            "cost_score": 97,
            "max_amount": 999999999,
            "risk_level": "VERY_LOW",
            "regulatory_overhead": "LOW",
            "capacity_per_hour": 1000000,
            "availability": 0.9999,
            "processing_time": "1-2 days"
        },
        "SEPA_Direct_Debit": {
            "type": "DOMESTIC_RECURRING",
            "success_rate": 0.995,
            "avg_cost_usd": 0.10,
            "speed_score": 40,
            "cost_score": 98,
            "max_amount": 999999999,
            "risk_level": "MEDIUM",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500000,
            "availability": 0.997,
            "processing_time": "Varies"
        },
        "SWIFT_GPI": {
            "type": "CROSS_BORDER_EXPRESS",
            "success_rate": 0.98,
            "avg_cost_usd": 32.00,
            "speed_score": 95,
            "cost_score": 30,
            "max_amount": 999999999,
            "risk_level": "LOW",
            "regulatory_overhead": "HIGH",
            "capacity_per_hour": 500,
            "availability": 0.995,
            "processing_time": "2-4 hours"
        },
        "SWIFT_TRADITIONAL": {
            "type": "CROSS_BORDER_STANDARD",
            "success_rate": 0.97,
            "avg_cost_usd": 25.00,
            "speed_score": 60,
            "cost_score": 45,
            "max_amount": 999999999,
            "risk_level": "LOW",
            "regulatory_overhead": "MEDIUM",
            "capacity_per_hour": 500,
            "availability": 0.985,
            "processing_time": "3-5 days"
        }
    },
    "corridors": {
        "EU_EU": ["SEPA_CT", "SEPA_INST", "TARGET2", "SEPA_Batch", "SEPA_Direct_Debit"],
        "EU_US": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "EU_GB": ["SEPA_CT", "SWIFT_GPI"],
        "US_EU": ["SWIFT_GPI", "SWIFT_TRADITIONAL"],
        "GB_EU": ["SEPA_CT", "SWIFT_GPI"]
    }
}

# ============================================================
# REGION REGISTRY
# ============================================================
REGIONS = {
    "ZA": SOUTH_AFRICA_REGION,
    "US": UNITED_STATES_REGION,
    "GB": UNITED_KINGDOM_REGION,
    "EU": EUROPE_REGION
}

def get_region(region_code: str):
    """Get region configuration by code"""
    region = REGIONS.get(region_code.upper())
    if not region:
        raise ValueError(f"Unknown region: {region_code}. Available: {list(REGIONS.keys())}")
    return region

def get_all_regions():
    """Get all available regions"""
    return {code: region["name"] for code, region in REGIONS.items()}

def get_region_payment_types(region_code: str):
    """Get payment types for a region"""
    region = get_region(region_code)
    return region["payment_types"]

def get_region_rails(region_code: str):
    """Get payment rails for a region"""
    region = get_region(region_code)
    return region["rails"]

def get_region_corridors(region_code: str):
    """Get payment corridors for a region"""
    region = get_region(region_code)
    return region["corridors"]

def get_region_currency(region_code: str):
    """Get domestic currency for a region"""
    region = get_region(region_code)
    return region["domestic_currency"]
