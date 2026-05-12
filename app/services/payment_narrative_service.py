from __future__ import annotations
from agents.state import PaymentState


class PaymentNarrativeService:
    """
    Generates a structured compliance narrative / audit report
    for a completed payment, matching the compliance officer's review format.
    """

    def generate_full_report(self, state: PaymentState) -> dict:
        return {
            "payment": {
                "payment_id": state.get("payment_id"),
                "state_key": state.get("state_key"),
                "amount": state.get("amount"),
                "currency_from": state.get("currency_from"),
                "currency_to": state.get("currency_to"),
                "corridor": f"{state.get('sender_country')} → {state.get('receiver_country')}",
                "sender": state.get("sender_name"),
                "receiver": state.get("receiver_name"),
                "purpose": state.get("payment_purpose"),
                "routing_preference": state.get("routing_preference"),
            },
            "compliance": {
                "status": state.get("compliance_status"),
                "risk_score": state.get("risk_score"),
                "aml_cleared": state.get("aml_cleared"),
                "sanctions_cleared": state.get("sanctions_cleared"),
                "sanctions_check_status": state.get("sanctions_check_status"),
                "fraud_check_score": state.get("fraud_check_score"),
                "notes": state.get("compliance_notes"),
                "violations": state.get("validation_violations", []),
                "warnings": state.get("validation_warnings", []),
            },
            "routing": {
                "selected_rail": state.get("selected_rail"),
                "backup_rail": state.get("backup_rail"),
                "optimization_reasoning": state.get("optimization_reasoning"),
                "fx_rate": state.get("fx_rate"),
                "fx_rate_details": state.get("fx_rate_details"),
            },
            "layer4": {
                "validation_status": state.get("layer4_validation_status"),
                "balance_check": state.get("layer4_balance_check"),
                "account_status": state.get("layer4_account_status"),
                "confirmation": state.get("layer4_confirmation"),
                "reconciliation": state.get("layer4_reconciliation"),
            },
            "execution": {
                "status": state.get("execution_status"),
                "execution_time": state.get("execution_time"),
                "original_format": state.get("original_message_format"),
                "converted_format": state.get("converted_message_format"),
                "conversion_time_ms": state.get("conversion_time_ms"),
            },
            "feedback": {
                "actual_cost": state.get("actual_cost"),
                "actual_processing_time": state.get("actual_processing_time"),
                "success": state.get("success"),
                "performance_delta": state.get("performance_delta"),
                "notes": state.get("feedback_notes"),
            },
        }
