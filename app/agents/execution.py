"""
Agent 4: Execution
Responsibility: Channel routing and failover
"""

import time
import random
from typing import Dict

class ExecutionAgent:
    """Executes payment through selected channel with failover"""
    
    def __init__(self):
        # Message format templates
        self.format_templates = {
            "SWIFT_GPI": self._format_swift_gpi,
            "TAG": self._format_tag,
            "BANKSERV": self._format_bankserv,
            "CORRESPONDENT": self._format_correspondent,
            "RTGS": self._format_rtgs
        }
    
    def execute_payment(self, state: Dict) -> Dict:
        """
        Execute payment through selected rail
        
        Returns:
            Dict with execution status and formatted message
        """
        print("\n[Agent 4: Execution] Starting payment execution...")
        start_time = time.time()
        
        selected_rail = state["selected_rail"]
        backup_rail = state.get("backup_rail", "NONE")
        
        if selected_rail == "NONE":
            return {
                "execution_status": "FAILED",
                "formatted_message": {},
                "rail_response": {"error": "No rail selected"},
                "execution_time": 0
            }
        
        # Format message for selected rail
        formatted_message = self._format_message(selected_rail, state)
        print(f"  ✓ Message formatted for {selected_rail}")
        
        # Attempt execution
        success, rail_response = self._execute_on_rail(selected_rail, formatted_message)
        
        # Failover if primary fails and backup exists
        if not success and backup_rail != "NONE":
            print(f"  ⚠ Primary rail failed, attempting failover to {backup_rail}")
            formatted_message = self._format_message(backup_rail, state)
            success, rail_response = self._execute_on_rail(backup_rail, formatted_message)
            selected_rail = backup_rail if success else selected_rail
        
        execution_time = time.time() - start_time
        
        status = "SUCCESS" if success else "FAILED"
        print(f"  ✓ Execution {status} via {selected_rail}")
        print(f"  ✓ Execution completed in {execution_time:.3f}s")
        
        return {
            "execution_status": status,
            "formatted_message": formatted_message,
            "rail_response": rail_response,
            "execution_time": execution_time
        }
    
    def _format_message(self, rail: str, state: Dict) -> Dict:
        """Format payment message for specific rail"""
        formatter = self.format_templates.get(rail, self._format_generic)
        return formatter(state)
    
    def _format_swift_gpi(self, state: Dict) -> Dict:
        """Format SWIFT GPI message (MT103)"""
        return {
            "format": "SWIFT_MT103",
            "fields": {
                "20": f"TRN{state['payment_id'][-10:]}",  # Transaction Reference
                "23B": "CRED",  # Bank Operation Code
                "32A": f"{self._format_date()}{state['currency_to']}{state['amount']:.2f}",  # Value Date, Currency, Amount
                "50K": self._truncate_field(state["sender_name"], 35, 4),  # Ordering Customer
                "59": self._truncate_field(state["receiver_name"], 35, 4),  # Beneficiary
                "70": self._truncate_field(state["payment_purpose"], 35, 4),  # Remittance Info
                "71A": "OUR",  # Charges (OUR/SHA/BEN)
            },
            "character_set": "SWIFT_X",
            "validation": "SWIFT_FIN"
        }
    
    def _format_tag(self, state: Dict) -> Dict:
        """Format TAG (SADC-RTGS) message"""
        return {
            "format": "TAG_XML",
            "fields": {
                "MsgId": f"TAG{state['payment_id'][-16:]}",
                "CreDtTm": self._format_iso_datetime(),
                "IntrBkSttlmAmt": {
                    "Ccy": state["currency_to"],
                    "Value": state["amount"]
                },
                "Dbtr": {
                    "Nm": state["sender_name"][:140]
                },
                "Cdtr": {
                    "Nm": state["receiver_name"][:140]
                },
                "RmtInf": {
                    "Ustrd": state["payment_purpose"][:140]
                }
            },
            "schema": "ISO20022_pacs.008",
            "validation": "XML_SCHEMA"
        }
    
    def _format_bankserv(self, state: Dict) -> Dict:
        """Format BANKSERV ACB message (fixed-length)"""
        return {
            "format": "BANKSERV_ACB",
            "record": {
                "record_type": "010",
                "account_number": "9" * 10,  # Mock
                "amount": f"{int(state['amount'] * 100):015d}",  # Amount in cents, 15 digits
                "transaction_code": "30",
                "beneficiary_name": state["receiver_name"][:32].ljust(32),
                "reference": state["payment_purpose"][:20].ljust(20)
            },
            "length": 280,
            "encoding": "ASCII"
        }
    
    def _format_correspondent(self, state: Dict) -> Dict:
        """Format correspondent bank message"""
        return {
            "format": "CORRESPONDENT_PROPRIETARY",
            "fields": {
                "reference": state["payment_id"],
                "amount": state["amount"],
                "currency": state["currency_to"],
                "sender": state["sender_name"],
                "receiver": state["receiver_name"],
                "purpose": state["payment_purpose"],
                "instructions": "CORRESPONDENT_ROUTING"
            }
        }
    
    def _format_rtgs(self, state: Dict) -> Dict:
        """Format RTGS message"""
        return {
            "format": "RTGS_XML",
            "fields": {
                "PaymentId": state["payment_id"],
                "Amount": state["amount"],
                "Currency": state["currency_to"],
                "Debtor": state["sender_name"],
                "Creditor": state["receiver_name"],
                "Purpose": state["payment_purpose"]
            },
            "settlement": "REAL_TIME_GROSS"
        }
    
    def _format_generic(self, state: Dict) -> Dict:
        """Generic message format"""
        return {
            "format": "GENERIC",
            "payment_id": state["payment_id"],
            "amount": state["amount"],
            "currency": state["currency_to"],
            "sender": state["sender_name"],
            "receiver": state["receiver_name"]
        }
    
    def _execute_on_rail(self, rail: str, message: Dict) -> tuple:
        """
        Execute payment on specific rail
        
        Returns:
            (success: bool, response: Dict)
        """
        # Simulate rail execution with realistic success rates
        rail_success_rates = {
            "SWIFT_GPI": 0.98,
            "TAG": 0.96,
            "BANKSERV": 0.99,
            "CORRESPONDENT": 0.94,
            "RTGS": 0.97
        }
        
        success_rate = rail_success_rates.get(rail, 0.95)
        success = random.random() < success_rate
        
        # Simulate processing delay
        time.sleep(0.1)
        
        if success:
            response = {
                "status": "ACCEPTED",
                "rail": rail,
                "confirmation_id": f"{rail}-{random.randint(100000, 999999)}",
                "timestamp": self._format_iso_datetime(),
                "estimated_settlement": "2025-11-11T10:00:00Z"
            }
        else:
            response = {
                "status": "REJECTED",
                "rail": rail,
                "error_code": random.choice(["TIMEOUT", "INVALID_FORMAT", "INSUFFICIENT_FUNDS"]),
                "error_message": "Simulated failure for testing",
                "timestamp": self._format_iso_datetime()
            }
        
        return success, response
    
    def _truncate_field(self, text: str, max_length: int, max_lines: int) -> str:
        """Truncate text to SWIFT field limits"""
        # Simple truncation - production would be more sophisticated
        lines = []
        remaining = text
        
        for _ in range(max_lines):
            if len(remaining) <= max_length:
                lines.append(remaining)
                break
            lines.append(remaining[:max_length])
            remaining = remaining[max_length:]
        
        return "\n".join(lines)
    
    def _format_date(self) -> str:
        """Format date as YYMMDD"""
        from datetime import datetime
        return datetime.now().strftime("%y%m%d")
    
    def _format_iso_datetime(self) -> str:
        """Format datetime as ISO 8601"""
        from datetime import datetime
        return datetime.now().isoformat() + "Z"
