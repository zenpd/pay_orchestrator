"""
Policy Reasoner Agent
Responsibility: Compliance and regulatory validation
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """Compliance validation result."""
    status: str  # "APPROVED", "HOLD_FOR_REVIEW", "REJECTED"
    risk_score: float  # 0-1.0
    compliance_checks: Dict[str, bool]
    risk_factors: List[str]
    compliance_notes: str
    warnings: List[str]


class PolicyReasonerAgent:
    """Validates payment compliance with regional regulations."""
    
    def __init__(self):
        """Initialize compliance rules and regulatory requirements."""
        self.country_rules = self._init_country_rules()
        self.high_risk_countries = ["ZW", "IR", "KP", "SY", "CU"]
        self.sanctions_list = self._init_sanctions_list()
        self.risk_weights = {
            "amount_threshold": 0.25,
            "high_risk_country": 0.20,
            "sanctions_risk": 0.30,
            "corridor_restrictions": 0.15,
            "compliance_requirement": 0.10
        }
    
    def _init_country_rules(self) -> Dict:
        """Initialize country-specific compliance rules."""
        return {
            "US": {
                "max_transaction_limit": 100000,
                "requires_purpose_code": True,
                "requires_tax_id": True,
                "ofac_screening": True,
                "supported_corridors": ["US_UK", "US_EU", "US_CA"],
                "reporting_requirements": ["FinCEN", "FATCA"]
            },
            "UK": {
                "max_transaction_limit": 150000,
                "requires_purpose_code": False,
                "requires_tax_id": False,
                "ofac_screening": True,
                "supported_corridors": ["UK_US", "UK_EU", "UK_ZA"],
                "reporting_requirements": ["FCA", "HMRC"]
            },
            "SA": {
                "max_transaction_limit": 1000000,
                "requires_purpose_code": True,
                "requires_tax_id": True,
                "ofac_screening": False,
                "supported_corridors": ["ZA_UK", "ZA_EU", "ZA_US"],
                "reporting_requirements": ["SARB", "CIPC"]
            },
            "EUR": {
                "max_transaction_limit": 50000,  # Stricter for SEPA
                "requires_purpose_code": True,
                "requires_tax_id": True,
                "ofac_screening": True,
                "supported_corridors": ["EU_US", "EU_UK", "EU_ZA"],
                "reporting_requirements": ["ECB", "BaFin"]
            }
        }
    
    def _init_sanctions_list(self) -> List[str]:
        """Initialize sanctions list (mock - would connect to OFAC/EU sanctions DB)."""
        return [
            "SANCTIONED ENTITY LLC",
            "BLOCKED COMPANY INC",
            "PROHIBITED TRADING CORP",
            "RESTRICTED BANK LLC"
        ]
    
    def validate_payment_compliance(self, 
                                    amount: float,
                                    currency: str,
                                    sender_country: str,
                                    receiver_country: str,
                                    corridor: str,
                                    sender_name: str = None,
                                    receiver_name: str = None) -> ComplianceResult:
        """
        Comprehensive compliance validation.
        
        Args:
            amount: Transaction amount
            currency: Currency code (USD, GBP, EUR, ZAR)
            sender_country: Sender country code
            receiver_country: Receiver country code
            corridor: Route (e.g., US_UK)
            sender_name: Sender entity name (for sanctions screening)
            receiver_name: Receiver entity name (for sanctions screening)
        
        Returns:
            ComplianceResult with validation status and reasoning
        """
        checks = {}
        risk_factors = []
        warnings = []
        
        # 1. Sanctions screening
        sanctions_cleared = True
        if sender_name or receiver_name:
            sanctions_cleared = self._screen_sanctions(sender_name, receiver_name)
            if not sanctions_cleared:
                risk_factors.append("SANCTIONS_ALERT")
                warnings.append(f"Sender/Receiver may match sanctions list")
        checks["sanctions_screening"] = sanctions_cleared
        
        # 2. High-risk country check
        high_risk = self._check_high_risk_countries(sender_country, receiver_country)
        if high_risk:
            risk_factors.append("HIGH_RISK_COUNTRY")
            warnings.append(f"Transaction involves high-risk jurisdiction(s)")
        checks["high_risk_countries"] = not high_risk
        
        # 3. Transaction limits check
        limits_ok = self._check_transaction_limits(amount, sender_country)
        if not limits_ok:
            risk_factors.append("LIMIT_EXCEEDED")
            warnings.append(f"Amount exceeds regulatory limit for {sender_country}")
        checks["transaction_limits"] = limits_ok
        
        # 4. Corridor compliance check
        corridor_ok = self._validate_corridor_compliance(corridor, sender_country, receiver_country)
        if not corridor_ok:
            risk_factors.append("CORRIDOR_RESTRICTED")
            warnings.append(f"Corridor {corridor} not supported from {sender_country}")
        checks["corridor_compliance"] = corridor_ok
        
        # 5. Country-specific rules
        country_rules_ok = self._validate_country_rules(
            sender_country, amount, sender_name, receiver_name
        )
        if not country_rules_ok:
            risk_factors.append("COUNTRY_RULES_VIOLATION")
            warnings.append(f"Transaction violates {sender_country} regulations")
        checks["country_rules"] = country_rules_ok
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(checks, risk_factors)
        
        # Determine compliance status
        if risk_score >= 0.7:
            status = "REJECTED"
            compliance_notes = f"High compliance risk ({risk_score:.2f}): {', '.join(risk_factors)}"
        elif risk_score >= 0.4:
            status = "HOLD_FOR_REVIEW"
            compliance_notes = f"Manual review required. Risk factors: {', '.join(risk_factors)}"
        else:
            status = "APPROVED"
            compliance_notes = "All compliance checks passed"
        
        # Add warnings for borderline cases
        if 0.3 <= risk_score < 0.4:
            warnings.append("Close to review threshold - monitor for patterns")
        
        return ComplianceResult(
            status=status,
            risk_score=risk_score,
            compliance_checks=checks,
            risk_factors=risk_factors,
            compliance_notes=compliance_notes,
            warnings=warnings
        )
    
    def _screen_sanctions(self, sender: str, receiver: str) -> bool:
        """Screen entities against sanctions list."""
        if not sender and not receiver:
            return True
        
        sender_upper = (sender or "").upper()
        receiver_upper = (receiver or "").upper()
        
        for sanctioned in self.sanctions_list:
            if sanctioned in sender_upper or sanctioned in receiver_upper:
                return False
        return True
    
    def _check_high_risk_countries(self, sender_country: str, receiver_country: str) -> bool:
        """Identify high-risk country involvement."""
        return sender_country in self.high_risk_countries or \
               receiver_country in self.high_risk_countries
    
    def _check_transaction_limits(self, amount: float, country: str) -> bool:
        """Validate transaction against country limits."""
        if country not in self.country_rules:
            return True  # Default approve if rules not defined
        
        max_limit = self.country_rules[country].get("max_transaction_limit", float('inf'))
        return amount <= max_limit
    
    def _validate_corridor_compliance(self, corridor: str, sender_country: str, 
                                     receiver_country: str) -> bool:
        """Check if corridor is supported from sender country."""
        if sender_country not in self.country_rules:
            return True  # Default approve
        
        supported = self.country_rules[sender_country].get("supported_corridors", [])
        if not supported:
            return True  # No restrictions
        
        return corridor in supported or corridor.replace("_", "").upper() in \
               [c.replace("_", "").upper() for c in supported]
    
    def _validate_country_rules(self, country: str, amount: float,
                               sender_name: str, receiver_name: str) -> bool:
        """Validate country-specific requirements."""
        if country not in self.country_rules:
            return True
        
        rules = self.country_rules[country]
        
        # Check if purpose code is required
        if rules.get("requires_purpose_code") and not sender_name:
            return False  # Would normally require purpose code
        
        # Check if tax ID is required
        if rules.get("requires_tax_id") and not sender_name:
            return False  # Would normally require tax ID
        
        return True
    
    def _calculate_risk_score(self, checks: Dict[str, bool], 
                            risk_factors: List[str]) -> float:
        """Calculate overall compliance risk score (0-1.0)."""
        base_score = sum(1 for passed in checks.values() if not passed) / len(checks)
        
        # Weight by risk factors
        factor_scores = {
            "SANCTIONS_ALERT": 0.30,
            "HIGH_RISK_COUNTRY": 0.15,
            "LIMIT_EXCEEDED": 0.20,
            "CORRIDOR_RESTRICTED": 0.15,
            "COUNTRY_RULES_VIOLATION": 0.20
        }
        
        factor_score = sum(factor_scores.get(f, 0.10) for f in risk_factors) / max(len(risk_factors), 1)
        
        # Combined score: 60% checks, 40% factors
        return (base_score * 0.6) + (factor_score * 0.4)
