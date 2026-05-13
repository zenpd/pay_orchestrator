"""
Regional payment data and corridors with realistic mock data.
Supports: US, UK, SA (South Africa), EUR (Europe)
"""
from typing import Dict, List, Any
from enum import Enum


class Region(str, Enum):
    """Supported regions."""
    US = "US"
    UK = "UK"
    SA = "SA"
    EUR = "EUR"


# ============================================================================
# REGIONAL PAYMENT RAILS
# ============================================================================

REGIONAL_RAILS: Dict[Region, Dict[str, Dict[str, Any]]] = {
    Region.US: {
        "ACH": {
            "name": "ACH (Automated Clearing House)",
            "type": "DOMESTIC_BATCH",
            "speed_score": 65,
            "cost_score": 95,  # Cheapest
            "reliability_score": 88,
            "estimated_cost_usd": 0.50,
            "estimated_time_hours": 24.0,
            "success_rate": 0.98,
            "max_amount": 100000,
            "min_amount": 1,
            "supported_corridors": ["US_CA", "US_MX", "US_UK", "US_INTL"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "Wire_Transfer": {
            "name": "Wire Transfer (Fedwire)",
            "type": "DOMESTIC_URGENT",
            "speed_score": 95,
            "cost_score": 40,
            "reliability_score": 99,
            "estimated_cost_usd": 15.00,
            "estimated_time_hours": 0.5,
            "success_rate": 0.995,
            "max_amount": 999999999,
            "min_amount": 1,
            "supported_corridors": ["US_CA", "US_MX", "US_UK", "US_INTL", "US_FAST"],
            "liquidity_requirement": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": True,
        },
        "RealTimePayments": {
            "name": "Real-Time Payments (RTP)",
            "type": "DOMESTIC_INSTANT",
            "speed_score": 100,
            "cost_score": 80,
            "reliability_score": 92,
            "estimated_cost_usd": 2.50,
            "estimated_time_hours": 0.02,  # ~1 minute
            "success_rate": 0.94,
            "max_amount": 500000,
            "min_amount": 1,
            "supported_corridors": ["US_CA", "US_MX", "US_FAST"],
            "liquidity_requirement": "LOW",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": False,
        },
        "SWIFT_International": {
            "name": "SWIFT (International)",
            "type": "CROSS_BORDER",
            "speed_score": 85,
            "cost_score": 35,
            "reliability_score": 96,
            "estimated_cost_usd": 25.00,
            "estimated_time_hours": 1.0,
            "success_rate": 0.99,
            "max_amount": 999999999,
            "min_amount": 100,
            "supported_corridors": ["US_UK", "US_INTL", "US_EUR"],
            "liquidity_requirement": "HIGH",
            "regulatory_overhead": "HIGH",
            "supports_high_value": True,
        },
        "Remittance_Services": {
            "name": "Remittance (MoneyGram/Western Union)",
            "type": "CROSS_BORDER_REMITTANCE",
            "speed_score": 88,
            "cost_score": 25,
            "reliability_score": 90,
            "estimated_cost_usd": 3.99,
            "estimated_time_hours": 0.25,  # 15 minutes
            "success_rate": 0.97,
            "max_amount": 10000,
            "min_amount": 1,
            "supported_corridors": ["US_CA", "US_MX"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": False,
        },
    },

    Region.UK: {
        "Faster_Payments": {
            "name": "Faster Payments",
            "type": "DOMESTIC_RAPID",
            "speed_score": 88,
            "cost_score": 85,
            "reliability_score": 91,
            "estimated_cost_usd": 1.25,
            "estimated_time_hours": 0.083,  # 5 minutes
            "success_rate": 0.96,
            "max_amount": 500000,
            "min_amount": 1,
            "supported_corridors": ["UK_EU", "UK_US", "UK_FAST"],
            "liquidity_requirement": "LOW",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "BACS": {
            "name": "BACS (Bankers' Automated Clearing Services)",
            "type": "DOMESTIC_BATCH",
            "speed_score": 60,
            "cost_score": 92,
            "reliability_score": 99,
            "estimated_cost_usd": 0.75,
            "estimated_time_hours": 48.0,
            "success_rate": 0.998,
            "max_amount": 50000,
            "min_amount": 1,
            "supported_corridors": ["UK_EU", "UK_US"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "CHAPS": {
            "name": "CHAPS (Clearing House Automated Payment System)",
            "type": "DOMESTIC_HIGH_VALUE",
            "speed_score": 95,
            "cost_score": 30,
            "reliability_score": 99,
            "estimated_cost_usd": 8.00,
            "estimated_time_hours": 0.25,  # ~15 minutes
            "success_rate": 0.997,
            "max_amount": 999999999,
            "min_amount": 1000,
            "supported_corridors": ["UK_EU", "UK_US", "UK_FAST"],
            "liquidity_requirement": "MEDIUM",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": True,
        },
        "SWIFT_GPI": {
            "name": "SWIFT GPI",
            "type": "CROSS_BORDER_EXPRESS",
            "speed_score": 92,
            "cost_score": 32,
            "reliability_score": 97,
            "estimated_cost_usd": 22.00,
            "estimated_time_hours": 0.5,
            "success_rate": 0.98,
            "max_amount": 999999999,
            "min_amount": 100,
            "supported_corridors": ["UK_EU", "UK_US", "UK_SA"],
            "liquidity_requirement": "HIGH",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": True,
        },
    },

    Region.SA: {
        "RTGS": {
            "name": "RTGS (Real Time Gross Settlement)",
            "type": "DOMESTIC_HIGH_VALUE",
            "speed_score": 90,
            "cost_score": 40,
            "reliability_score": 94,
            "estimated_cost_usd": 12.00,
            "estimated_time_hours": 1.0,
            "success_rate": 0.96,
            "max_amount": 50000000,
            "min_amount": 10000,
            "supported_corridors": ["SA_US", "SA_UK", "SA_EUR"],
            "liquidity_requirement": "HIGH",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": True,
        },
        "PayShap_Instant": {
            "name": "PayShap Instant",
            "type": "DOMESTIC_INSTANT",
            "speed_score": 98,
            "cost_score": 92,
            "reliability_score": 93,
            "estimated_cost_usd": 0.25,
            "estimated_time_hours": 0.001,  # 3.6 seconds
            "success_rate": 0.995,
            "max_amount": 50000,
            "min_amount": 1,
            "supported_corridors": ["SA_FAST", "SA_LOCAL"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "EFT": {
            "name": "EFT (Electronic Funds Transfer)",
            "type": "DOMESTIC_BATCH",
            "speed_score": 65,
            "cost_score": 88,
            "reliability_score": 92,
            "estimated_cost_usd": 0.50,
            "estimated_time_hours": 6.0,
            "success_rate": 0.98,
            "max_amount": 500000,
            "min_amount": 1,
            "supported_corridors": ["SA_LOCAL", "SA_FAST"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "SWIFT_GPI": {
            "name": "SWIFT GPI",
            "type": "CROSS_BORDER_EXPRESS",
            "speed_score": 85,
            "cost_score": 35,
            "reliability_score": 96,
            "estimated_cost_usd": 20.00,
            "estimated_time_hours": 2.0,
            "success_rate": 0.97,
            "max_amount": 999999999,
            "min_amount": 100,
            "supported_corridors": ["SA_US", "SA_UK", "SA_EUR"],
            "liquidity_requirement": "HIGH",
            "regulatory_overhead": "HIGH",
            "supports_high_value": True,
        },
        "Remittance": {
            "name": "Remittance Services (Local)",
            "type": "CROSS_BORDER_REMITTANCE",
            "speed_score": 80,
            "cost_score": 55,
            "reliability_score": 88,
            "estimated_cost_usd": 5.00,
            "estimated_time_hours": 0.5,
            "success_rate": 0.92,
            "max_amount": 5000,
            "min_amount": 1,
            "supported_corridors": ["SA_US", "SA_FAST"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": False,
        },
    },

    Region.EUR: {
        "SEPA_Instant": {
            "name": "SEPA Instant Credit Transfer",
            "type": "DOMESTIC_INSTANT",
            "speed_score": 98,
            "cost_score": 90,
            "reliability_score": 95,
            "estimated_cost_usd": 0.50,
            "estimated_time_hours": 0.01,  # 10 seconds
            "success_rate": 0.99,
            "max_amount": 100000,
            "min_amount": 1,
            "supported_corridors": ["EUR_FAST", "EUR_LOCAL"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "LOW",
            "supports_high_value": False,
        },
        "SEPA_Standard": {
            "name": "SEPA Credit Transfer",
            "type": "DOMESTIC_STANDARD",
            "speed_score": 70,
            "cost_score": 88,
            "reliability_score": 98,
            "estimated_cost_usd": 0.25,
            "estimated_time_hours": 24.0,
            "success_rate": 0.998,
            "max_amount": 50000,
            "min_amount": 1,
            "supported_corridors": ["EUR_LOCAL", "EUR_FAST"],
            "liquidity_requirement": "NONE",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": False,
        },
        "SWIFT_GPI": {
            "name": "SWIFT GPI",
            "type": "CROSS_BORDER_EXPRESS",
            "speed_score": 90,
            "cost_score": 38,
            "reliability_score": 96,
            "estimated_cost_usd": 18.00,
            "estimated_time_hours": 1.0,
            "success_rate": 0.98,
            "max_amount": 999999999,
            "min_amount": 100,
            "supported_corridors": ["EUR_US", "EUR_UK", "EUR_SA"],
            "liquidity_requirement": "HIGH",
            "regulatory_overhead": "MEDIUM",
            "supports_high_value": True,
        },
        "CHIPS": {
            "name": "Continuous Linked Settlement",
            "type": "CROSS_BORDER_HIGH_VALUE",
            "speed_score": 88,
            "cost_score": 28,
            "reliability_score": 97,
            "estimated_cost_usd": 30.00,
            "estimated_time_hours": 0.1,
            "success_rate": 0.995,
            "max_amount": 999999999,
            "min_amount": 50000,
            "supported_corridors": ["EUR_US", "EUR_SA"],
            "liquidity_requirement": "VERY_HIGH",
            "regulatory_overhead": "HIGH",
            "supports_high_value": True,
        },
    },
}

# ============================================================================
# REGIONAL CURRENCIES
# ============================================================================

REGIONAL_CURRENCIES: Dict[Region, List[str]] = {
    Region.US: ["USD", "EUR", "GBP", "CAD", "MXN", "ZAR", "AUD", "JPY"],
    Region.UK: ["GBP", "USD", "EUR", "CHF", "AUD", "CAD", "ZAR", "JPY"],
    Region.SA: ["ZAR", "USD", "EUR", "GBP", "AUD", "CAD", "GHS", "KES"],
    Region.EUR: ["EUR", "USD", "GBP", "CHF", "SEK", "NOK", "ZAR", "INR"],
}

# ============================================================================
# REGIONAL CORRIDORS
# ============================================================================

REGIONAL_CORRIDORS: Dict[Region, Dict[str, str]] = {
    Region.US: {
        "US_CA": "USA → Canada",
        "US_MX": "USA → Mexico",
        "US_UK": "USA → United Kingdom",
        "US_EUR": "USA → Europe",
        "US_INTL": "USA → International",
        "US_FAST": "USA → Fast Route",
    },
    Region.UK: {
        "UK_US": "UK → United States",
        "UK_EU": "UK → Europe",
        "UK_SA": "UK → South Africa",
        "UK_FAST": "UK → Fast Route",
        "UK_LOCAL": "UK → Local",
    },
    Region.SA: {
        "SA_US": "SA → United States",
        "SA_UK": "SA → United Kingdom",
        "SA_EUR": "SA → Europe",
        "SA_FAST": "SA → Fast Route",
        "SA_LOCAL": "SA → Local",
    },
    Region.EUR: {
        "EUR_US": "Europe → United States",
        "EUR_UK": "Europe → United Kingdom",
        "EUR_SA": "Europe → South Africa",
        "EUR_FAST": "Europe → Fast Route",
        "EUR_LOCAL": "Europe → Local",
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_rails_for_region(region: str) -> Dict[str, Dict[str, Any]]:
    """Get all available rails for a region."""
    try:
        return REGIONAL_RAILS[Region(region)]
    except KeyError:
        return REGIONAL_RAILS[Region.US]


def get_currencies_for_region(region: str) -> List[str]:
    """Get supported currencies for a region."""
    try:
        return REGIONAL_CURRENCIES[Region(region)]
    except KeyError:
        return REGIONAL_CURRENCIES[Region.US]


def get_corridors_for_region(region: str) -> Dict[str, str]:
    """Get available corridors for a region."""
    try:
        return REGIONAL_CORRIDORS[Region(region)]
    except KeyError:
        return REGIONAL_CORRIDORS[Region.US]


def score_rail_for_request(rail_data: Dict[str, Any], amount: float, corridor: str) -> float:
    """
    Calculate a composite score for a rail based on amount and corridor.
    
    Returns 0-100 score (higher is better).
    """
    # Check eligibility
    if amount > rail_data["max_amount"]:
        return 0  # Not eligible
    if amount < rail_data["min_amount"]:
        return 0  # Not eligible
    if corridor not in rail_data["supported_corridors"]:
        return 0  # Not eligible
    
    # Avoid high-value rails for small amounts (poor fit)
    if not rail_data["supports_high_value"] and amount > 100000:
        return rail_data["cost_score"] * 0.5  # Half score if not ideal
    
    # Weigh by importance: cost (30%), speed (40%), reliability (30%)
    composite = (
        rail_data["cost_score"] * 0.30 +
        rail_data["speed_score"] * 0.40 +
        rail_data["reliability_score"] * 0.30
    )
    
    return composite
