"""
Layer 4 Validator
Validates payment with both Payment Processing Systems and Backoffice Systems
BIDIRECTIONAL COMMUNICATION
"""

import time
from typing import Dict

class Layer4Validator:
    """
    Validates payment with Layer 4 systems before execution
    
    Layer 4 Components:
    - Payment Processing Systems: PayEx, ICM, BOLPES, Infinity, CIMS
    - Backoffice Systems: T24, Finacle, SAP, EE
    """
    
    def __init__(self):
        # Mock system availability
        self.systems_available = {
            # Payment Processing Systems
            "PayEx": True,
            "ICM": True,
            "BOLPES": True,
            "Infinity": True,
            "CIMS": True,
            # Backoffice Systems
            "T24": True,
            "Finacle": True,
            "SAP": True,
            "EE": True
        }
    
    def validate_payment(self, state: Dict) -> Dict:
        """
        Validate payment with Layer 4 systems (bidirectional)
        
        Returns:
            Dict with validation results from both payment processing
            and backoffice systems
        """
        print("\n[Layer 4: Pre-Execution Validation] Starting bidirectional validation...")
        start_time = time.time()
        
        amount = state.get("amount", 0)
        selected_rail = state.get("selected_rail", "UNKNOWN")
        
        # Validate with Backoffice Systems (balance checks)
        backoffice_validation = self._validate_backoffice_systems(state)
        
        # Validate with Payment Processing Systems (specialized checks)
        payment_processing_validation = self._validate_payment_processing_systems(
            state, 
            selected_rail
        )
        
        # Consolidate validation results
        validation_status = "APPROVED"
        validation_notes = []
        
        if not backoffice_validation["balance_sufficient"]:
            validation_status = "REJECTED"
            validation_notes.append("Insufficient balance")
        
        if not backoffice_validation["account_active"]:
            validation_status = "REJECTED"
            validation_notes.append("Account not active")
        
        if not payment_processing_validation["rail_ready"]:
            validation_status = "REJECTED"
            validation_notes.append(f"Rail {selected_rail} not ready")
        
        validation_time = time.time() - start_time
        
        print(f"  ✓ Backoffice Validation:")
        print(f"    - T24 Balance Check: {'PASS' if backoffice_validation['balance_sufficient'] else 'FAIL'}")
        print(f"    - Finacle Account Status: {'ACTIVE' if backoffice_validation['account_active'] else 'INACTIVE'}")
        print(f"    - SAP GL Balance: {backoffice_validation['gl_balance_status']}")
        print(f"  ✓ Payment Processing Validation:")
        print(f"    - {selected_rail} Rail Status: {'READY' if payment_processing_validation['rail_ready'] else 'NOT READY'}")
        print(f"    - Specialized Checks: {'PASS' if payment_processing_validation['specialized_checks'] else 'FAIL'}")
        print(f"  ✓ Overall Status: {validation_status}")
        print(f"  ✓ Validation completed in {validation_time:.3f}s")
        
        return {
            "layer4_validation_status": validation_status,
            "layer4_balance_check": backoffice_validation,
            "layer4_account_status": payment_processing_validation,
            "layer4_validation_notes": "; ".join(validation_notes) if validation_notes else "All checks passed"
        }
    
    def _validate_backoffice_systems(self, state: Dict) -> Dict:
        """
        Validate with Backoffice Systems (T24, Finacle, SAP, EE)
        
        Checks:
        - T24: Account balance verification
        - Finacle: Account status check
        - SAP: GL balance check
        - EE: FX limits check
        """
        amount = state.get("amount", 0)
        
        # Mock balance check (T24)
        available_balance = 500000.00  # Mock balance
        balance_sufficient = amount <= available_balance
        
        # Mock account status check (Finacle)
        account_active = True  # Mock - account is active
        account_not_frozen = True
        account_not_closed = True
        
        # Mock GL balance check (SAP)
        gl_balance_ok = True  # Mock - GL has sufficient balance
        
        # Mock FX limits check (EE)
        fx_limits_ok = True  # Mock - within FX limits
        
        return {
            "balance_sufficient": balance_sufficient,
            "available_balance": available_balance,
            "account_active": account_active and account_not_frozen and account_not_closed,
            "account_status_details": {
                "active": account_active,
                "frozen": not account_not_frozen,
                "closed": not account_not_closed
            },
            "gl_balance_status": "SUFFICIENT" if gl_balance_ok else "INSUFFICIENT",
            "fx_limits_ok": fx_limits_ok,
            "validated_by": ["T24", "Finacle", "SAP", "EE"]
        }
    
    def _validate_payment_processing_systems(self, state: Dict, rail: str) -> Dict:
        """
        Validate with Payment Processing Systems (PayEx, ICM, BOLPES, Infinity, CIMS)
        
        Checks rail-specific validations based on payment type
        """
        amount = state.get("amount", 0)
        currency_from = state.get("currency_from", "")
        currency_to = state.get("currency_to", "")
        
        # Determine which payment processing system to use
        processing_system = self._select_processing_system(rail, amount)
        
        # Rail readiness check
        rail_ready = self._check_rail_readiness(rail)
        
        # Specialized checks based on processing system
        specialized_checks = True
        specialized_notes = []
        
        if processing_system == "PayEx":
            # PayEx: FX and cross-border checks
            if currency_from != currency_to:
                specialized_checks = self._validate_fx_trade(currency_from, currency_to, amount)
                if not specialized_checks:
                    specialized_notes.append("FX validation failed")
        
        elif processing_system == "ICM":
            # ICM: Corporate payment aggregation checks
            specialized_checks = self._validate_corporate_limits(amount)
            if not specialized_checks:
                specialized_notes.append("Corporate limits exceeded")
        
        elif processing_system == "BOLPES":
            # BOLPES: Bulk payment checks
            specialized_checks = True  # Bulk payments generally approved
        
        return {
            "processing_system": processing_system,
            "rail_ready": rail_ready,
            "specialized_checks": specialized_checks,
            "specialized_notes": "; ".join(specialized_notes) if specialized_notes else "All checks passed"
        }
    
    def _select_processing_system(self, rail: str, amount: float) -> str:
        """Select appropriate payment processing system based on rail and amount"""
        if rail == "SWIFT_GPI":
            if amount > 100000:
                return "PayEx"
            else:
                return "ICM"
        elif rail == "BANKSERV":
            return "BOLPES"
        elif rail == "TAG":
            return "PayEx"
        else:
            return "ICM"
    
    def _check_rail_readiness(self, rail: str) -> bool:
        """Check if selected rail is ready for execution"""
        # Mock rail readiness check
        rail_status = {
            "SWIFT_GPI": True,
            "TAG": True,
            "BANKSERV": True,
            "CORRESPONDENT": True,
            "RTGS": True,
            "NAMPAY": True
        }
        return rail_status.get(rail, False)
    
    def _validate_fx_trade(self, currency_from: str, currency_to: str, amount: float) -> bool:
        """Validate FX trade parameters"""
        # Mock FX validation
        # In production: Check FX limits, spreads, etc.
        return True
    
    def _validate_corporate_limits(self, amount: float) -> bool:
        """Validate corporate payment limits"""
        # Mock corporate limit check
        corporate_limit = 1000000.00
        return amount <= corporate_limit
