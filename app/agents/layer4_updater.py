"""
Layer 4 Updater
Updates both Payment Processing Systems and Backoffice Systems post-execution
BIDIRECTIONAL COMMUNICATION
"""

import time
from typing import Dict
from datetime import datetime

class Layer4Updater:
    """
    Updates Layer 4 systems after payment execution
    
    Layer 4 Components:
    - Payment Processing Systems: PayEx, ICM, BOLPES, Infinity, CIMS
    - Backoffice Systems: T24, Finacle, SAP, EE
    """
    
    def __init__(self):
        pass
    
    def update_systems(self, state: Dict) -> Dict:
        """
        Update Layer 4 systems with execution results (bidirectional)
        
        Updates:
        - Payment Processing Systems: Transaction status, rail confirmations
        - Backoffice Systems: Account updates, GL posting, reconciliation
        
        Returns:
            Dict with update confirmations from all systems
        """
        print("\n[Layer 4: Post-Execution Updates] Starting bidirectional updates...")
        start_time = time.time()
        
        execution_status = state.get("execution_status", "UNKNOWN")
        selected_rail = state.get("selected_rail", "UNKNOWN")
        amount = state.get("amount", 0)
        rail_response = state.get("rail_response", {})
        
        # Update Backoffice Systems
        backoffice_updates = self._update_backoffice_systems(state)
        
        # Update Payment Processing Systems
        payment_processing_updates = self._update_payment_processing_systems(state)
        
        # Generate reconciliation data
        reconciliation = self._generate_reconciliation_data(state, backoffice_updates)
        
        update_time = time.time() - start_time
        
        print(f"  ✓ Backoffice System Updates:")
        print(f"    - T24: {backoffice_updates['t24_status']}")
        print(f"    - Finacle: {backoffice_updates['finacle_status']}")
        print(f"    - SAP: {backoffice_updates['sap_status']}")
        print(f"    - EE: {backoffice_updates['ee_status']}")
        print(f"  ✓ Payment Processing Updates:")
        print(f"    - {payment_processing_updates['system']}: {payment_processing_updates['status']}")
        print(f"  ✓ Reconciliation: {reconciliation['status']}")
        print(f"  ✓ Updates completed in {update_time:.3f}s")
        
        return {
            "layer4_confirmation": {
                "backoffice": backoffice_updates,
                "payment_processing": payment_processing_updates,
                "update_timestamp": datetime.now().isoformat()
            },
            "layer4_reconciliation": reconciliation
        }
    
    def _update_backoffice_systems(self, state: Dict) -> Dict:
        """
        Update Backoffice Systems (T24, Finacle, SAP, EE)
        
        Updates:
        - T24: Post transaction, update account balance
        - Finacle: Update transaction history
        - SAP: Post to GL, update reconciliation
        - EE: Update FX position if applicable
        """
        payment_id = state.get("payment_id", "")
        amount = state.get("amount", 0)
        execution_status = state.get("execution_status", "UNKNOWN")
        currency_from = state.get("currency_from", "")
        currency_to = state.get("currency_to", "")
        
        # T24 Update: Post transaction and update balance
        t24_update = self._update_t24(payment_id, amount, execution_status)
        
        # Finacle Update: Update transaction history
        finacle_update = self._update_finacle(payment_id, amount, execution_status)
        
        # SAP Update: Post to GL and reconciliation
        sap_update = self._update_sap(payment_id, amount, execution_status)
        
        # EE Update: FX position update if cross-currency
        ee_update = self._update_ee(currency_from, currency_to, amount, execution_status)
        
        return {
            "t24_status": t24_update["status"],
            "t24_transaction_id": t24_update["transaction_id"],
            "finacle_status": finacle_update["status"],
            "finacle_history_updated": finacle_update["history_updated"],
            "sap_status": sap_update["status"],
            "sap_gl_document": sap_update["gl_document"],
            "ee_status": ee_update["status"],
            "ee_fx_updated": ee_update["fx_updated"]
        }
    
    def _update_payment_processing_systems(self, state: Dict) -> Dict:
        """
        Update Payment Processing Systems (PayEx, ICM, BOLPES, Infinity, CIMS)
        
        Updates transaction status in the appropriate processing system
        """
        selected_rail = state.get("selected_rail", "")
        payment_id = state.get("payment_id", "")
        execution_status = state.get("execution_status", "UNKNOWN")
        amount = state.get("amount", 0)
        
        # Determine which system to update based on rail
        if selected_rail == "SWIFT_GPI":
            if amount > 100000:
                system = "PayEx"
            else:
                system = "ICM"
        elif selected_rail == "BANKSERV":
            system = "BOLPES"
        elif selected_rail == "TAG":
            system = "PayEx"
        else:
            system = "ICM"
        
        # Update the processing system
        update_status = "UPDATED" if execution_status == "SUCCESS" else "FAILED"
        
        return {
            "system": system,
            "status": update_status,
            "payment_id": payment_id,
            "update_timestamp": datetime.now().isoformat()
        }
    
    def _update_t24(self, payment_id: str, amount: float, status: str) -> Dict:
        """Update T24 core banking system"""
        # Mock T24 update
        if status == "SUCCESS":
            return {
                "status": "POSTED",
                "transaction_id": f"T24-{payment_id[-10:]}",
                "balance_updated": True
            }
        else:
            return {
                "status": "FAILED",
                "transaction_id": None,
                "balance_updated": False
            }
    
    def _update_finacle(self, payment_id: str, amount: float, status: str) -> Dict:
        """Update Finacle core banking system"""
        # Mock Finacle update
        if status == "SUCCESS":
            return {
                "status": "UPDATED",
                "history_updated": True,
                "history_id": f"FIN-{payment_id[-10:]}"
            }
        else:
            return {
                "status": "FAILED",
                "history_updated": False,
                "history_id": None
            }
    
    def _update_sap(self, payment_id: str, amount: float, status: str) -> Dict:
        """Update SAP ERP/Financial system"""
        # Mock SAP update
        if status == "SUCCESS":
            return {
                "status": "GL_POSTED",
                "gl_document": f"SAP-GL-{payment_id[-8:]}",
                "reconciliation_status": "PENDING"
            }
        else:
            return {
                "status": "FAILED",
                "gl_document": None,
                "reconciliation_status": "N/A"
            }
    
    def _update_ee(self, currency_from: str, currency_to: str, amount: float, status: str) -> Dict:
        """Update EE (Enterprise Exchange) system"""
        # Mock EE update
        if status == "SUCCESS" and currency_from != currency_to:
            return {
                "status": "FX_UPDATED",
                "fx_updated": True,
                "position_updated": True
            }
        elif status == "SUCCESS":
            return {
                "status": "NO_FX_UPDATE_NEEDED",
                "fx_updated": False,
                "position_updated": False
            }
        else:
            return {
                "status": "FAILED",
                "fx_updated": False,
                "position_updated": False
            }
    
    def _generate_reconciliation_data(self, state: Dict, backoffice_updates: Dict) -> Dict:
        """Generate reconciliation data for nostro/vostro accounts"""
        payment_id = state.get("payment_id", "")
        amount = state.get("amount", 0)
        selected_rail = state.get("selected_rail", "")
        execution_status = state.get("execution_status", "UNKNOWN")
        
        if execution_status == "SUCCESS":
            reconciliation_status = "MATCHED"
            reconciliation_notes = "Transaction confirmed and reconciled"
        else:
            reconciliation_status = "UNMATCHED"
            reconciliation_notes = "Transaction failed - no reconciliation needed"
        
        return {
            "status": reconciliation_status,
            "payment_id": payment_id,
            "amount": amount,
            "rail": selected_rail,
            "t24_transaction_id": backoffice_updates.get("t24_transaction_id"),
            "sap_gl_document": backoffice_updates.get("sap_gl_document"),
            "reconciliation_notes": reconciliation_notes,
            "reconciliation_timestamp": datetime.now().isoformat()
        }
