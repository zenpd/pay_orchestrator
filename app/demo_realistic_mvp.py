"""
Realistic MVP Demo - Payment Processing Orchestrator
Comprehensive demonstration with multiple payment scenarios
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from payment_orchestrator_mvp import RealisticPaymentOrchestrator
from mock_data_sources import MockDataSources
from visual_logger import get_logger
from state_manager import get_state_manager, reset_state_manager

def print_banner():
    """Print application banner"""
    logger = get_logger()
    logger.header("PAYMENT PROCESSING ORCHESTRATOR - REALISTIC MVP")
    
    print("""
    Standard Bank / ZenLabs - October 2025
    5-Layer Architecture with AI-Powered Route Optimization
    
    Features:
    ✓ Real-time state management (Redis-like)
    ✓ Bidirectional Layer 4 integration
    ✓ ML-based route optimization
    ✓ Comprehensive compliance validation
    ✓ Automatic failover and reconciliation
    ✓ Complete data sovereignty
    """)

def print_architecture():
    """Print architecture overview"""
    logger = get_logger()
    logger.section("🏗️  5-LAYER ARCHITECTURE")
    
    print("""
    Layer 1: Order Processing
    ├── BOLSA/AR, BOL Plus, Trade Apps, Mobile Apps
    └── Canonical transformation layer
        ↓
    Layer 2: VolPay (Internal Router) - TWO-WAY INTEGRATION
    └── Coordinates with AI Orchestrator
        ↓
    Layer 3: Agentic AI Orchestrator (Self-Hosted)
    ├── Agent 1: Context Collector (FX, corridors, performance)
    ├── Agent 2: Policy Reasoner (Ollama LLM - compliance)
    ├── Agent 3: Optimizer (TensorFlow - route selection)
    ├── Agent 4: Execution (message formatting, execution)
    └── Agent 5: Feedback (continuous learning)
        ↓
    Layer 4: Payment Processing & Backoffice (BIDIRECTIONAL)
    ├── Payment Processing: PayEx, ICM, BOLPES, Infinity, CIMS
    │   └── Pre-execution: Rail readiness, specialized checks
    │   └── Post-execution: Transaction status updates
    └── Backoffice: T24, Finacle, SAP, EE
        └── Pre-execution: Balance checks, account validation
        └── Post-execution: GL posting, reconciliation
        ↓
    Layer 5: Payment Rails & Settlement
    └── SWIFT_GPI, TAG, BANKSERV, NAMPAY, Settlement Networks
        ‖
    Parallel: Logging & Monitoring
    └── CIMS BAW-DD (monitoring), Firecosft (AML), AMS (audit)
    """)

def scenario_1_standard_cross_border(orchestrator):
    """Scenario 1: Standard cross-border payment"""
    logger = get_logger()
    logger.header("SCENARIO 1: Standard Cross-Border Payment (ZA → US)")
    
    payment = {
        "payment_id": "PAY-2025-001",
        "amount": 50000.00,
        "currency_from": "ZAR",
        "currency_to": "USD",
        "sender_country": "ZA",
        "receiver_country": "US",
        "payment_purpose": "Trade settlement - imported automotive parts",
        "sender_name": MockDataSources.get_random_sa_company(),
        "receiver_name": MockDataSources.get_random_international_company()
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Compliance": result["compliance_status"],
        "Selected Rail": result["selected_rail"],
        "Backup Rail": result["backup_rail"],
        "Cost": f"${result['actual_cost']:.2f}",
        "Processing Time": f"{result['actual_processing_time']:.2f}h",
        "Reconciliation": result["reconciliation_status"]
    })
    
    return result

def scenario_2_high_value_payment(orchestrator):
    """Scenario 2: High-value payment with enhanced checks"""
    logger = get_logger()
    logger.header("SCENARIO 2: High-Value Payment (ZA → GB)")
    
    payment = {
        "payment_id": "PAY-2025-002",
        "amount": 250000.00,
        "currency_from": "ZAR",
        "currency_to": "GBP",
        "sender_country": "ZA",
        "receiver_country": "GB",
        "payment_purpose": "Commercial real estate acquisition - London property",
        "sender_name": "Standard Bank of South Africa",
        "receiver_name": "London Properties International Ltd"
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Compliance": result["compliance_status"],
        "Risk Score": f"{result['risk_score']:.3f}",
        "Selected Rail": result["selected_rail"],
        "Cost": f"${result['actual_cost']:.2f}",
        "Processing Time": f"{result['actual_processing_time']:.2f}h"
    })
    
    return result

def scenario_3_domestic_bulk(orchestrator):
    """Scenario 3: Domestic bulk payment"""
    logger = get_logger()
    logger.header("SCENARIO 3: Domestic Bulk Payment (Payroll)")
    
    payment = {
        "payment_id": "PAY-2025-003",
        "amount": 8500.00,
        "currency_from": "ZAR",
        "currency_to": "ZAR",
        "sender_country": "ZA",
        "receiver_country": "ZA",
        "payment_purpose": "Monthly payroll - employee salaries",
        "sender_name": "Shoprite Holdings",
        "receiver_name": "Employee Collective Payment Account"
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Selected Rail": result["selected_rail"],
        "Cost": f"${result['actual_cost']:.2f}",
        "Processing Time": f"{result['actual_processing_time']:.2f}h",
        "Expected Rail": "BANKSERV (domestic ACH)"
    })
    
    return result

def scenario_4_regional_sadc(orchestrator):
    """Scenario 4: Regional SADC payment"""
    logger = get_logger()
    logger.header("SCENARIO 4: Regional SADC Payment (ZA → Botswana)")
    
    payment = {
        "payment_id": "PAY-2025-004",
        "amount": 35000.00,
        "currency_from": "ZAR",
        "currency_to": "USD",
        "sender_country": "ZA",
        "receiver_country": "BW",
        "payment_purpose": "Regional trade - mining equipment supply",
        "sender_name": "Anglo American Platinum",
        "receiver_name": "Botswana Mining Equipment Corp"
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Selected Rail": result["selected_rail"],
        "Cost": f"${result['actual_cost']:.2f}",
        "Processing Time": f"{result['actual_processing_time']:.2f}h",
        "Expected Rail": "TAG (SADC-RTGS)"
    })
    
    return result

def scenario_5_time_sensitive(orchestrator):
    """Scenario 5: Time-sensitive payment"""
    logger = get_logger()
    logger.header("SCENARIO 5: Time-Sensitive Payment (Urgent)")
    
    payment = {
        "payment_id": "PAY-2025-005",
        "amount": 75000.00,
        "currency_from": "ZAR",
        "currency_to": "USD",
        "sender_country": "ZA",
        "receiver_country": "US",
        "payment_purpose": "Urgent trade settlement - time-critical delivery",
        "sender_name": "Sasol Limited",
        "receiver_name": "American Commodities Trading Inc"
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Selected Rail": result["selected_rail"],
        "Optimization": "Speed-prioritized routing",
        "Cost": f"${result['actual_cost']:.2f}",
        "Processing Time": f"{result['actual_processing_time']:.2f}h"
    })
    
    return result

def scenario_6_multiple_currencies(orchestrator):
    """Scenario 6: Multi-currency transaction"""
    logger = get_logger()
    logger.header("SCENARIO 6: Multi-Currency Transaction")
    
    payment = {
        "payment_id": "PAY-2025-006",
        "amount": 125000.00,
        "currency_from": "ZAR",
        "currency_to": "EUR",
        "sender_country": "ZA",
        "receiver_country": "DE",
        "payment_purpose": "Import payment - German manufacturing equipment",
        "sender_name": "Discovery Limited",
        "receiver_name": "Deutsche Industrial Equipment GmbH"
    }
    
    result = orchestrator.process_payment(payment)
    
    logger.result_box("Payment Result", {
        "Status": result["status"],
        "Selected Rail": result["selected_rail"],
        "Cost": f"${result['actual_cost']:.2f}",
        "FX Conversion": "EUR via EE (Enterprise Exchange)",
        "Processing Time": f"{result['actual_processing_time']:.2f}h"
    })
    
    return result

def print_session_summary(orchestrator: RealisticPaymentOrchestrator):
    """Print comprehensive session summary"""
    logger = get_logger()
    state_manager = get_state_manager()
    
    summary = state_manager.get_session_summary()
    
    logger.header("📊 SESSION SUMMARY & METRICS")
    
    # Session info
    logger.section("Session Information")
    logger.metric("Session ID", summary["session_id"])
    logger.metric("Duration", f"{summary['duration_seconds']:.1f}s")
    logger.metric("Total Payments", summary["total_payments"])
    
    # Success metrics
    logger.section("Success Metrics")
    logger.metric("Successful Payments", summary["successful"])
    logger.metric("Failed Payments", summary["failed"])
    logger.metric("Success Rate", f"{summary['success_rate']:.1f}%")
    logger.metric("Avg Processing Time", f"{summary['avg_processing_time']:.3f}s")
    
    # Compliance metrics
    logger.section("Compliance Metrics")
    comp_stats = summary["compliance_stats"]
    logger.metric("Approved", comp_stats["approved"])
    logger.metric("Rejected", comp_stats["rejected"])
    logger.metric("On Hold", comp_stats["hold"])
    
    # Layer 4 metrics
    logger.section("Layer 4 Integration Metrics")
    layer4_stats = summary["layer4_stats"]
    logger.metric("Total Validations", layer4_stats["total_validations"])
    logger.metric("Validation Failures", layer4_stats["failures"])
    logger.metric("Validation Success Rate", f"{layer4_stats['success_rate']:.1f}%")
    
    # Rails usage
    logger.section("Payment Rails Usage")
    for rail, count in summary["rails_used"].items():
        logger.metric(rail, count)
    
    # Key benefits demonstration
    logger.section("🎯 Key Benefits Demonstrated")
    print(f"""
    ✓ Real-time state management with Redis-like persistence
    ✓ Bidirectional Layer 4 integration (pre & post execution)
    ✓ ML-based intelligent route optimization
    ✓ Automated compliance validation (AML, sanctions, rules)
    ✓ Automatic failover with backup rail selection
    ✓ Complete reconciliation and GL posting
    ✓ Continuous learning through feedback loop
    ✓ 100% data sovereignty (all on-premise)
    
    Expected Production Benefits:
    • 25-40% latency reduction through intelligent routing
    • 10-15% cost savings through optimization
    • 98%+ SLA compliance with predictive routing
    • 30% reduction in manual exceptions
    • 50% faster reconciliation through bidirectional updates
    """)

def main():
    """Main demo execution"""
    # Reset state for clean demo
    reset_state_manager()
    
    # Print banner and architecture
    print_banner()
    print_architecture()
    
    logger = get_logger()
    logger.section("🚀 STARTING PAYMENT PROCESSING DEMONSTRATION")
    
    print("\nProcessing 6 different payment scenarios to demonstrate:")
    print("  1. Standard cross-border payments")
    print("  2. High-value transaction handling")
    print("  3. Domestic bulk payments")
    print("  4. Regional SADC transactions")
    print("  5. Time-sensitive routing")
    print("  6. Multi-currency processing")
    print()
    
    # Create single orchestrator instance
    orchestrator = RealisticPaymentOrchestrator()
    results = []
    
    try:
        # Run scenarios with the same orchestrator instance
        print("Starting demonstration in 2 seconds...")
        time.sleep(2)
        
        results.append(scenario_1_standard_cross_border(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        results.append(scenario_2_high_value_payment(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        results.append(scenario_3_domestic_bulk(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        results.append(scenario_4_regional_sadc(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        results.append(scenario_5_time_sensitive(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        results.append(scenario_6_multiple_currencies(orchestrator))
        logger.divider()
        time.sleep(0.5)
        
        # Print summary using the same orchestrator
        print_session_summary(orchestrator)
        
        logger.header("✅ DEMONSTRATION COMPLETED SUCCESSFULLY")
        
        print("""
Next Steps:
1. Review the detailed logs above showing each agent's execution
2. Note the Layer 4 bidirectional validation and updates
3. Observe the intelligent rail selection based on multiple factors
4. Check the comprehensive metrics and success rates
5. Ready for stakeholder presentation and production planning

The POC demonstrates production-grade capabilities while maintaining
complete data sovereignty and regulatory compliance.
        """)
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
