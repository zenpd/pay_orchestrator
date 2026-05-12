"""
Payment Processing Agentic AI Orchestrator - PoC Implementation
5-Layer Architecture with left-shifted validations, MT→MX conversion, PoC rails
"""

from typing import TypedDict, Annotated, Sequence, Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator
import time
import random
import hashlib
from datetime import datetime

from state_manager import get_state_manager
from mock_data_sources import MockDataSources
from visual_logger import get_logger

# Import agents
from agents.context_collector import ContextCollectorAgent
from agents.policy_reasoner import PolicyReasonerAgent
from agents.optimizer import OptimizerAgent
from agents.execution import ExecutionAgent
from agents.feedback import FeedbackAgent
from agents.layer4_validator import Layer4Validator
from agents.layer4_updater import Layer4Updater


class PaymentState(TypedDict):
    """Enhanced state with PoC-specific fields"""
    # State management
    state_key: str
    payment_id: str
    
    # Input data (Layer 1)
    amount: float
    currency_from: str
    currency_to: str
    sender_country: str
    receiver_country: str
    payment_purpose: str
    sender_name: str
    receiver_name: str
    routing_preference: str  # NEW: "fastest" or "cheapest"
    
    # Context enrichment (Agent 1)
    fx_rate: float
    fx_rate_details: dict
    corridor_metadata: dict
    rail_performance: dict
    predicted_processing_times: dict
    validation_rules: dict  # NEW: Left-shifted pre-validation rules
    
    # Compliance & Pre-Validation (Agent 2)
    compliance_status: str
    risk_score: float
    aml_cleared: bool
    sanctions_cleared: bool
    compliance_notes: str
    compliance_details: dict
    # NEW: PoC validation results
    validation_violations: List[str]
    validation_warnings: List[str]
    fraud_check_score: float
    sanctions_check_status: str
    
    # Optimization (Agent 3)
    selected_rail: str
    backup_rail: str
    routing_score: dict
    optimization_reasoning: str
    
    # Layer 4 validation
    layer4_balance_check: dict
    layer4_account_status: dict
    layer4_validation_status: str
    layer4_validation_details: dict
    
    # Execution (Agent 4)
    execution_status: str
    formatted_message: dict
    rail_response: dict
    execution_time: float
    execution_details: dict
    # NEW: MT→MX conversion tracking
    original_message_format: str
    converted_message_format: str
    conversion_time_ms: float
    
    # Layer 4 updates
    layer4_confirmation: dict
    layer4_reconciliation: dict
    
    # Feedback (Agent 5)
    actual_cost: float
    actual_processing_time: float
    success: bool
    feedback_notes: str
    performance_delta: dict
    
    # Workflow control
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str


class RealisticPaymentOrchestrator:
    """
    PoC Orchestrator with left-shifted validations, MT→MX, PoC rails
    """
    
    def __init__(self):
        self.state_manager = get_state_manager()
        self.logger = get_logger()
        self.data_sources = MockDataSources()
        
        # Initialize agents
        self.agents = {
            "context_collector": ContextCollectorAgent(),
            "policy_reasoner": PolicyReasonerAgent(),
            "optimizer": OptimizerAgent(),
            "layer4_validator": Layer4Validator(),
            "execution": ExecutionAgent(),
            "layer4_updater": Layer4Updater(),
            "feedback": FeedbackAgent()
        }
        
        # Build graph
        self.graph = self._build_graph()
        
        print("✓ PoC Orchestrator initialized")
        print(f"  • {len(self.agents)} agents loaded")
        print(f"  • PoC rails: PayShap, RTGS, SWIFT, SADC, Partners")
        print(f"  • Left-shifted validations enabled")
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph"""
        workflow = StateGraph(PaymentState)
        
        # Add nodes
        workflow.add_node("context_collector", self.context_collector_agent)
        workflow.add_node("policy_reasoner", self.policy_reasoner_agent)
        workflow.add_node("optimizer", self.optimizer_agent)
        workflow.add_node("layer4_validation", self.layer4_validation)
        workflow.add_node("execution", self.execution_agent)
        workflow.add_node("layer4_update", self.layer4_update)
        workflow.add_node("feedback", self.feedback_agent)
        
        # Define workflow
        workflow.set_entry_point("context_collector")
        workflow.add_edge("context_collector", "policy_reasoner")
        workflow.add_conditional_edges(
            "policy_reasoner",
            self._compliance_router,
            {
                "approved": "optimizer",
                "rejected": END,
                "hold": END
            }
        )
        workflow.add_edge("optimizer", "layer4_validation")
        workflow.add_conditional_edges(
            "layer4_validation",
            self._layer4_router,
            {
                "approved": "execution",
                "rejected": END
            }
        )
        workflow.add_edge("execution", "layer4_update")
        workflow.add_edge("layer4_update", "feedback")
        workflow.add_edge("feedback", END)
        
        return workflow.compile()
    
    def _compliance_router(self, state: PaymentState) -> str:
        """Route based on compliance status"""
        status = state.get("compliance_status", "HOLD")
        
        if status == "APPROVED":
            return "approved"
        elif status == "REJECTED":
            self.logger.error(f"✗ Pre-validation failed: {state.get('compliance_notes', '')}")
            return "rejected"
        else:
            self.logger.warning(f"⚠ Payment on hold for manual review")
            return "hold"
    
    def _layer4_router(self, state: PaymentState) -> str:
        """Route based on Layer 4 validation"""
        status = state.get("layer4_validation_status", "REJECTED")
        
        if status == "APPROVED":
            return "approved"
        else:
            self.logger.error("✗ Layer 4 validation failed - payment rejected")
            return "rejected"
    
    def context_collector_agent(self, state: PaymentState) -> PaymentState:
        """Agent 1: Collect context including validation rules"""
        print(f"\n[Agent 1: Context Collector] Gathering data...")
        time.sleep(random.uniform(0.1, 0.3))
        
        result = self.agents["context_collector"].collect_context(state)
        
        # Add validation rules
        result["validation_rules"] = self.data_sources.get_validation_rules()
        
        state.update(result)
        
        self.state_manager.update_payment_state(
            state["state_key"],
            "context_collection",
            result,
            "IN_PROGRESS"
        )
        
        print(f"✓ FX Rate: {state['fx_rate']:.6f}")
        print(f"✓ Corridor: {state['sender_country']}_{state['receiver_country']}")
        print(f"✓ Available Rails: {len(state['corridor_metadata']['available_rails'])}")
        
        return state
    
    def policy_reasoner_agent(self, state: PaymentState) -> PaymentState:
        """Agent 2: PoC Pre-Validation (Left-Shifted)"""
        print(f"\n[Agent 2: Pre-Validator] Running left-shifted validations...")
        time.sleep(random.uniform(0.2, 0.5))
        
        violations = []
        warnings = []
        
        # Get validation rules
        rules = state["validation_rules"]["business_rules"]
        
        # 1. Amount Check
        if rules["amount_check"]["enabled"]:
            max_amount = rules["amount_check"]["max_amount"]
            if state["amount"] > max_amount:
                violations.append(f"Amount {state['amount']} exceeds limit {max_amount}")
        
        # 2. Holiday Check
        if rules["holiday_check"]["enabled"]:
            today = datetime.now().strftime("%Y-%m-%d")
            if today in rules["holiday_check"]["blocked_dates"]:
                warnings.append("⚠ Today is a banking holiday")
        
        # 3. Cut-off Check
        if rules["cutoff_check"]["enabled"]:
            cutoff = rules["cutoff_check"]["cutoff_time"]
            current_time = datetime.now().strftime("%H:%M")
            if current_time > cutoff:
                warnings.append(f"⚠ After cut-off {cutoff} - will batch next day")
        
        # 4. Sanctions Check (Rail validation)
        if state["validation_rules"]["payment_rail_validations"]["sanctions_check"]["enabled"]:
            if self.data_sources.is_sanctioned(state["receiver_name"]):
                violations.append("❌ SANCTIONS_VIOLATION")
                sanctions_status = "FAILED"
            else:
                sanctions_status = "PASSED"
        else:
            sanctions_status = "SKIPPED"
        
        # 5. Fraud Check
        if state["validation_rules"]["payment_rail_validations"]["fraud_check"]["enabled"]:
            # Simulate ML model scoring
            fraud_score = random.random() * 0.3  # 0-0.3 = low risk
            if fraud_score > 0.7:
                violations.append(f"❌ HIGH_FRAUD_RISK (score: {fraud_score:.2f})")
        else:
            fraud_score = 0.0
        
        # Determine compliance status
        if violations:
            compliance_status = "REJECTED"
            notes = f"Pre-validation failed: {'; '.join(violations)}"
        elif warnings:
            compliance_status = "ON_HOLD"
            notes = f"Manual review needed: {'; '.join(warnings)}"
        else:
            compliance_status = "APPROVED"
            notes = "All pre-validations passed"
        
        result = {
            "compliance_status": compliance_status,
            "compliance_notes": notes,
            "validation_violations": violations,
            "validation_warnings": warnings,
            "sanctions_check_status": sanctions_status,
            "fraud_check_score": fraud_score,
            "risk_score": fraud_score + (0.3 if violations else 0),
            "sanctions_cleared": sanctions_status == "PASSED",
            "aml_cleared": len(violations) == 0
        }
        
        state.update(result)
        self.state_manager.update_payment_state(state["state_key"], "pre_validation", result, "IN_PROGRESS")
        
        print(f"✓ Compliance: {compliance_status}")
        print(f"✓ Violations: {len(violations)}")
        print(f"✓ Warnings: {len(warnings)}")
        
        return state
    
    def optimizer_agent(self, state: PaymentState) -> PaymentState:
        """Agent 3: AI-Driven Rail Selection with Multi-Rail Scoring"""
        print(f"\n[Agent 3: Optimizer] Evaluating {len(state['corridor_metadata']['available_rails'])} rails...")
        time.sleep(random.uniform(0.1, 0.3))
        
        corridor_data = state["corridor_metadata"]
        available_rails = corridor_data["available_rails"]
        
        if not available_rails:
            return state
        
        # Get preference parameters (defaults for backward compatibility)
        preference = state.get("routing_preference", "fastest")
        urgency = state.get("urgency", 5)
        risk_tolerance = state.get("risk_tolerance", 7)
        
        # Score each rail
        scored_rails = []
        for rail_name in available_rails:
            rail_perf = state["rail_performance"].get(rail_name, {})
            
            # Skip if rail can't handle the amount
            max_amount = rail_perf.get("max_amount", 0)
            if state["amount"] > max_amount:
                continue
            
            # Base scores
            speed_score = rail_perf.get("speed_score", 50)
            cost_score = rail_perf.get("cost_score", 50)
            
            # Apply preference weighting
            if preference == "fastest":
                speed_weight = 0.7 + (urgency / 50)  # 0.7-0.9
                cost_weight = 1 - speed_weight
            elif preference == "cheapest":
                cost_weight = 0.7 + (risk_tolerance / 50)  # 0.7-0.9
                speed_weight = 1 - cost_weight
            else:  # balanced
                speed_weight = 0.5 + (urgency / 100) - (risk_tolerance / 200)
                cost_weight = 1 - speed_weight
            
            # Calculate weighted base score
            base_score = (speed_score * speed_weight) + (cost_score * cost_weight)
            
            # Apply penalties
            risk_penalties = {"VERY_LOW": 0, "LOW": 5, "MEDIUM": 15, "HIGH": 30}
            reg_penalties = {"LOW": 0, "MEDIUM": 5, "HIGH": 12}
            
            risk_penalty = risk_penalties.get(rail_perf.get("risk_level", "MEDIUM"), 10)
            reg_penalty = reg_penalties.get(rail_perf.get("regulatory_overhead", "MEDIUM"), 5)
            
            # Risk tolerance reduces penalty impact
            risk_penalty = risk_penalty * (1 - risk_tolerance / 15)
            
            final_score = max(0, base_score - risk_penalty - reg_penalty)
            
            scored_rails.append({
                "rail": rail_name,
                "final_score": final_score,
                "speed_score": speed_score,
                "cost_score": cost_score,
                "risk_penalty": risk_penalty,
                "regulatory_penalty": reg_penalty,
                "speed_weight": speed_weight,
                "cost_weight": cost_weight,
                "attributes": {
                    "speed_score": speed_score,
                    "cost_score": cost_score,
                    "risk_level": rail_perf.get("risk_level", "MEDIUM"),
                    "regulatory_overhead": rail_perf.get("regulatory_overhead", "MEDIUM")
                }
            })
        
        # Sort by final score
        scored_rails.sort(key=lambda x: x['final_score'], reverse=True)
        
        if not scored_rails:
            raise ValueError("No suitable rails available for this payment")
        
        selected = scored_rails[0]
        runner_up = scored_rails[1] if len(scored_rails) > 1 else None
        
        # Generate justification
        if selected['speed_score'] > selected['cost_score'] and urgency > 6:
            reason = f"Highest speed score ({selected['speed_score']}) matches urgent requirement"
        elif selected['cost_score'] > selected['speed_score'] and preference == "cheapest":
            reason = f"Best cost efficiency ({selected['cost_score']}) matches preference"
        elif selected['attributes']['risk_level'] == "VERY_LOW" and risk_tolerance < 5:
            reason = "Lowest risk level preferred for risk-averse profile"
        else:
            reason = f"Best overall weighted score ({selected['final_score']:.1f})"
        
        result = {
            "selected_rail": selected['rail'],
            "backup_rail": runner_up['rail'] if runner_up else selected['rail'],
            "optimization_reasoning": reason,
            "routing_score": {
                "preference_applied": preference,
                "scoring_method": f"Weighted: {selected['speed_weight']:.0%} speed, {selected['cost_weight']:.0%} cost",
                "all_scored_rails": scored_rails,
                "selected": {
                    "rail": selected['rail'],
                    "score": round(selected['final_score'], 1),
                    "attributes": selected['attributes']
                },
                "runner_up": {
                    "rail": runner_up['rail'],
                    "score": round(runner_up['final_score'], 1),
                    "margin": round(selected['final_score'] - runner_up['final_score'], 1)
                } if runner_up else None
            }
        }
        
        state.update(result)
        self.state_manager.record_metric("rails_used", selected['rail'])
        self.state_manager.update_payment_state(state["state_key"], "optimization", result, "IN_PROGRESS")
        
        print(f"✓ Selected: {selected['rail']} (Score: {selected['final_score']:.1f})")
        if runner_up:
            print(f"✓ Runner-up: {runner_up['rail']} (Margin: +{selected['final_score'] - runner_up['final_score']:.1f})")
        
        return state

    def layer4_validation(self, state: PaymentState) -> PaymentState:
        """Layer 4: Pre-execution validation"""
        print(f"\n[Layer 4: Pre-Execution] Validating with back-office...")
        time.sleep(random.uniform(0.3, 0.6))
        
        result = self.agents["layer4_validator"].validate_payment(state)
        
        if result["layer4_validation_status"] != "APPROVED":
            self.state_manager.record_metric("layer4_validation_failures", 1)
        
        state.update(result)
        self.state_manager.update_payment_state(state["state_key"], "layer4_validation", result, "IN_PROGRESS")
        
        print(f"✓ Layer 4 Status: {result['layer4_validation_status']}")
        
        return state
    
    def execution_agent(self, state: PaymentState) -> PaymentState:
        """Agent 4: Execution with MT→MX Conversion"""
        print(f"\n[Agent 4: Execution] Processing through {state['selected_rail']}...")
        time.sleep(random.uniform(0.2, 0.5))
        
        # Simulate MT→MX conversion
        if "SWIFT" in state["selected_rail"]:
            original_format = "MT103"
            converted_format = "MX"
            conversion_time_ms = 150
            conversion_msg = "MT→MX conversion completed"
        elif "PayShap" in state["selected_rail"] or "RTGS" in state["selected_rail"]:
            original_format = "MX"
            converted_format = "MX"
            conversion_time_ms = 0
            conversion_msg = "Native MX format"
        else:
            original_format = "CUSTOM"
            converted_format = "CUSTOM"
            conversion_time_ms = 0
            conversion_msg = "Partner-specific format"
        
        result = self.agents["execution"].execute_payment(state)
        
        # Add conversion details
        result.update({
            "original_message_format": original_format,
            "converted_message_format": converted_format,
            "conversion_time_ms": conversion_time_ms,
            "conversion_message": conversion_msg
        })
        
        state.update(result)
        self.state_manager.update_payment_state(state["state_key"], "execution", result, "IN_PROGRESS")
        
        print(f"✓ Execution: {result['execution_status']}")
        print(f"✓ Format: {conversion_msg}")
        
        return state
    
    def layer4_update(self, state: PaymentState) -> PaymentState:
        """Layer 4: Post-execution updates"""
        print(f"\n[Layer 4: Post-Execution] Updating back-office...")
        time.sleep(random.uniform(0.2, 0.4))
        
        result = self.agents["layer4_updater"].update_systems(state)
        state.update(result)
        self.state_manager.update_payment_state(state["state_key"], "layer4_update", result, "IN_PROGRESS")
        
        print(f"✓ Back-office updated")
        
        return state
    
    def feedback_agent(self, state: PaymentState) -> PaymentState:
        """Agent 5: Feedback & Learning"""
        print(f"\n[Agent 5: Feedback] Collecting metrics...")
        time.sleep(random.uniform(0.1, 0.2))
        
        result = self.agents["feedback"].process_feedback(state)
        state.update(result)
        self.state_manager.update_payment_state(state["state_key"], "feedback", result, "COMPLETED")
        
        print(f"✓ Cost: ${result['actual_cost']:.2f}")
        print(f"✓ Time: {result['actual_processing_time']:.2f}h")
        
        return state
    
    def process_payment(self, payment_data: dict) -> dict:
        """Main payment processing entry point"""
        start_time = time.time()
        
        # Add routing preference if not present
        payment_data.setdefault("routing_preference", "fastest")
        
        # Create state
        state_key = self.state_manager.create_payment_state(
            payment_data["payment_id"],
            payment_data
        )
        
        initial_state = {
            "routing_preference": payment_data.get("routing_preference", "fastest"),
            "urgency": payment_data.get("urgency", 5),
            "risk_tolerance": payment_data.get("risk_tolerance", 7),
            "state_key": state_key,
            "payment_id": payment_data["payment_id"],
            "amount": payment_data["amount"],
            "currency_from": payment_data["currency_from"],
            "currency_to": payment_data["currency_to"],
            "sender_country": payment_data["sender_country"],
            "receiver_country": payment_data["receiver_country"],
            "payment_purpose": payment_data["payment_purpose"],
            "sender_name": payment_data["sender_name"],
            "receiver_name": payment_data["receiver_name"],
            "routing_preference": payment_data["routing_preference"],
            "messages": [],
            "next_step": "context_collector",
            # Initialize all fields
            "fx_rate": 0.0, "fx_rate_details": {}, "corridor_metadata": {}, "rail_performance": {},
            "validation_rules": {}, "compliance_status": "PENDING", "risk_score": 0.0,
            "validation_violations": [], "validation_warnings": [], "fraud_check_score": 0.0,
            "sanctions_check_status": "PENDING", "selected_rail": "", "backup_rail": "",
            "layer4_validation_status": "PENDING", "execution_status": "PENDING",
            "original_message_format": "", "converted_message_format": "",
            "conversion_time_ms": 0, "actual_cost": 0.0, "actual_processing_time": 0.0,
            "success": False
        }
        
        # Log payment
        self.logger.payment_summary({
            "Payment ID": payment_data["payment_id"],
            "Amount": f"{payment_data['currency_from']} {payment_data['amount']:,.2f}",
            "Corridor": f"{payment_data['sender_country']} → {payment_data['receiver_country']}",
            "Purpose": payment_data["payment_purpose"],
            "Sender": payment_data["sender_name"],
            "Receiver": payment_data["receiver_name"],
            "Routing Preference": payment_data["routing_preference"]
        })
        
        # Process
        try:
            print(f"\n🔄 Starting PoC payment processing...")
            final_state = self.graph.invoke(initial_state)
            
            processing_time = time.time() - start_time
            
            # Finalize
            success = final_state.get("execution_status") == "SUCCESS"
            self.state_manager.finalize_payment(state_key, success, processing_time)
            
            result = self._format_result(final_state, processing_time)
            
            print(f"✅ PoC Processing: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            processing_time = time.time() - start_time
            self.state_manager.finalize_payment(state_key, False, processing_time)
            
            return {
                "payment_id": payment_data["payment_id"],
                "state_key": state_key,
                "status": "FAILED",
                "compliance_status": "PENDING",
                "layer4_validation": "PENDING",
                "selected_rail": "",
                "backup_rail": "",
                "risk_score": 0.0,
                "actual_cost": 0.0,
                "actual_processing_time": 0.0,
                "success": False,
                "total_processing_time": processing_time,
                "reconciliation_status": "PENDING",
                "error": str(e)
            }
    
    def _format_result(self, state: PaymentState, processing_time: float) -> dict:
        """Format PoC result"""
        return {
            "payment_id": state["payment_id"],
            "state_key": state["state_key"],
            "status": state.get("execution_status", "UNKNOWN"),
            "compliance_status": state.get("compliance_status", "PENDING"),
            "layer4_validation": state.get("layer4_validation_status", "PENDING"),
            "selected_rail": state.get("selected_rail", "NONE"),
            "backup_rail": state.get("backup_rail", "NONE"),
            "risk_score": state.get("risk_score", 0.0),
            "validation_violations": state.get("validation_violations", []),
            "validation_warnings": state.get("validation_warnings", []),
            "fraud_check_score": state.get("fraud_check_score", 0.0),
            "sanctions_check_status": state.get("sanctions_check_status", "PENDING"),
            "actual_cost": state.get("actual_cost", 0.0),
            "actual_processing_time": state.get("actual_processing_time", 0.0),
            "success": state.get("success", False),
            "total_processing_time": processing_time,
            "reconciliation_status": state.get("layer4_reconciliation", {}).get("status", "PENDING"),
            "message_conversion": {
                "original": state.get("original_message_format", ""),
                "converted": state.get("converted_message_format", ""),
                "conversion_time_ms": state.get("conversion_time_ms", 0)
            },
            "eft_replacement_ready": state.get("rail_performance", {}).get(state.get("selected_rail"), {}).get("eft_replacement_ready", False)
        }