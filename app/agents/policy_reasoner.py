"""
Agent 2: Policy Reasoner
Responsibility: Compliance validation using local LLM inference
"""

import time
import re
from typing import Dict, List

class PolicyReasonerAgent:
    """Validates compliance using rule engine and LLM reasoning"""
    
    def __init__(self):
        # Sanctions list (mock)
        self.sanctions_list = self._init_sanctions_list()
        
        # High-risk countries
        self.high_risk_countries = ["ZW", "IR", "KP", "SY", "CU"]
        
        # Country-specific rules
        self.country_rules = self._init_country_rules()
    
    def _init_sanctions_list(self) -> List[str]:
        """Initialize sanctions list (mock)"""
        return [
            "SANCTIONED ENTITY LLC",
            "BLOCKED COMPANY INC",
            "PROHIBITED TRADING CORP"
        ]
    
    def _init_country_rules(self) -> Dict:
        """Initialize country-specific compliance rules"""
        return {
            "US": {
                "max_transaction_limit": 100000,
                "requires_purpose_code": True,
                "requires_tax_id": True,
                "ofac_screening": True,
                "finra_reporting": True
            },
            "GB": {
                "max_transaction_limit": 150000,
                "requires_purpose_code": False,
                "requires_tax_id": False,
                "ofac_screening": True,
                "finra_reporting": False
            },
            "ZA": {
                "max_transaction_limit": 1000000,
                "requires_purpose_code": True,
                "requires_tax_id": True,
                "ofac_screening": False,
                "sarb_reporting": True
            }
        }
    
    def validate_compliance(self, state: Dict) -> Dict:
        """
        Validate payment compliance
        
        Returns:
            Dict with compliance status and risk score
        """
        print("\n[Agent 2: Policy Reasoner] Starting compliance validation...")
        start_time = time.time()
        
        compliance_checks = []
        risk_factors = []
        
        # 1. Sanctions screening
        aml_cleared = self._screen_aml(state["sender_name"], state["receiver_name"])
        compliance_checks.append(("AML Screening", aml_cleared))
        if not aml_cleared:
            risk_factors.append("AML_ALERT")
        
        # 2. High-risk country check
        high_risk = self._check_high_risk_countries(
            state["sender_country"],
            state["receiver_country"]
        )
        compliance_checks.append(("High-Risk Countries", not high_risk))
        if high_risk:
            risk_factors.append("HIGH_RISK_COUNTRY")
        
        # 3. Country-specific rules
        country_compliance = self._validate_country_rules(state)
        compliance_checks.append(("Country Rules", country_compliance["compliant"]))
        if not country_compliance["compliant"]:
            risk_factors.extend(country_compliance["violations"])
        
        # 4. Transaction limits
        limit_check = self._check_transaction_limits(state)
        compliance_checks.append(("Transaction Limits", limit_check))
        if not limit_check:
            risk_factors.append("LIMIT_EXCEEDED")
        
        # 5. LLM-based purpose analysis (mock Ollama inference)
        purpose_analysis = self._analyze_purpose_with_llm(state["payment_purpose"])
        compliance_checks.append(("Purpose Analysis", purpose_analysis["legitimate"]))
        if not purpose_analysis["legitimate"]:
            risk_factors.append("SUSPICIOUS_PURPOSE")
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(compliance_checks, risk_factors)
        
        # Determine final status
        if risk_score >= 0.8:
            compliance_status = "REJECTED"
            compliance_notes = f"High risk: {', '.join(risk_factors)}"
        elif risk_score >= 0.5:
            compliance_status = "HOLD_FOR_REVIEW"
            compliance_notes = f"Manual review required: {', '.join(risk_factors)}"
        else:
            compliance_status = "APPROVED"
            compliance_notes = "All compliance checks passed"
        
        validation_time = time.time() - start_time
        
        print(f"  ✓ AML Screening: {'CLEARED' if aml_cleared else 'ALERT'}")
        print(f"  ✓ Sanctions Check: {'CLEARED' if aml_cleared else 'BLOCKED'}")
        print(f"  ✓ Country Rules: {'COMPLIANT' if country_compliance['compliant'] else 'VIOLATIONS'}")
        print(f"  ✓ Risk Score: {risk_score:.2f}")
        print(f"  ✓ Status: {compliance_status}")
        print(f"  ✓ Validation completed in {validation_time:.3f}s")
        
        return {
            "compliance_status": compliance_status,
            "risk_score": risk_score,
            "aml_cleared": aml_cleared,
            "sanctions_cleared": aml_cleared,
            "compliance_notes": compliance_notes
        }
    
    def _screen_aml(self, sender: str, receiver: str) -> bool:
        """Screen sender and receiver against sanctions list"""
        sender_upper = sender.upper()
        receiver_upper = receiver.upper()
        
        for sanctioned in self.sanctions_list:
            if sanctioned in sender_upper or sanctioned in receiver_upper:
                return False
        
        return True
    
    def _check_high_risk_countries(self, sender_country: str, receiver_country: str) -> bool:
        """Check if transaction involves high-risk countries"""
        return sender_country in self.high_risk_countries or \
               receiver_country in self.high_risk_countries
    
    def _validate_country_rules(self, state: Dict) -> Dict:
        """Validate country-specific compliance rules"""
        receiver_country = state["receiver_country"]
        amount = state["amount"]
        
        if receiver_country not in self.country_rules:
            return {"compliant": True, "violations": []}
        
        rules = self.country_rules[receiver_country]
        violations = []
        
        # Check transaction limit
        if amount > rules.get("max_transaction_limit", float('inf')):
            violations.append(f"EXCEEDS_{receiver_country}_LIMIT")
        
        # Check purpose code requirement
        if rules.get("requires_purpose_code") and not state.get("payment_purpose"):
            violations.append("MISSING_PURPOSE_CODE")
        
        # Check tax ID requirement
        if rules.get("requires_tax_id"):
            violations.append("TAX_ID_VALIDATION_REQUIRED")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_transaction_limits(self, state: Dict) -> bool:
        """Check if transaction is within allowed limits"""
        amount = state["amount"]
        
        # Global limit check
        if amount > 500000:
            return False
        
        # Corridor-specific limits
        corridor_metadata = state.get("corridor_metadata", {})
        compliance_level = corridor_metadata.get("compliance_level", "MEDIUM")
        
        if compliance_level == "HIGH" and amount > 250000:
            return False
        
        return True
    
    def _analyze_purpose_with_llm(self, purpose: str) -> Dict:
        """
        Analyze payment purpose using LLM (mock Ollama inference)
        In production: Call Ollama API with Llama 2 or Mistral
        """
        # Mock LLM analysis
        suspicious_keywords = ["cash", "diamonds", "gold bullion", "bearer bonds", "shell company"]
        legitimate_keywords = ["trade", "invoice", "salary", "goods", "services", "settlement"]
        
        purpose_lower = purpose.lower()
        
        # Check for suspicious patterns
        has_suspicious = any(keyword in purpose_lower for keyword in suspicious_keywords)
        has_legitimate = any(keyword in purpose_lower for keyword in legitimate_keywords)
        
        if has_suspicious and not has_legitimate:
            return {
                "legitimate": False,
                "confidence": 0.85,
                "reasoning": "Contains suspicious keywords without clear legitimate purpose"
            }
        elif has_legitimate:
            return {
                "legitimate": True,
                "confidence": 0.92,
                "reasoning": "Contains legitimate business purpose indicators"
            }
        else:
            return {
                "legitimate": True,
                "confidence": 0.70,
                "reasoning": "No clear suspicious indicators, but purpose is vague"
            }
    
    def _calculate_risk_score(self, compliance_checks: List, risk_factors: List) -> float:
        """Calculate overall risk score"""
        # Base score from failed checks
        failed_checks = sum(1 for _, passed in compliance_checks if not passed)
        total_checks = len(compliance_checks)
        
        base_score = failed_checks / total_checks if total_checks > 0 else 0
        
        # Additional risk from specific factors
        critical_factors = ["AML_ALERT", "HIGH_RISK_COUNTRY", "SUSPICIOUS_PURPOSE"]
        critical_risk_count = sum(1 for factor in risk_factors if factor in critical_factors)
        
        # Boost score for critical risks
        risk_score = base_score + (critical_risk_count * 0.2)
        
        return min(risk_score, 1.0)  # Cap at 1.0
