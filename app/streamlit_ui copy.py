"""
Streamlit UI - Payment Processing Orchestrator (IMPROVED)
Interactive web interface with real-time logs and auto-refresh
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Payment Orchestrator",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .log-container {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        height: 500px;
        overflow-y: scroll;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_session_metrics():
    """Get current session metrics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/metrics/session")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_logs(last_n=100):
    """Get recent logs"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/logs?last_n={last_n}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def clear_logs():
    """Clear log buffer"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/logs/clear")
        return response.status_code == 200
    except:
        return False

def get_corridors():
    """Get available corridors"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/corridors")
        if response.status_code == 200:
            return response.json().get("corridors", [])
        return []
    except:
        return []

def get_rails():
    """Get rail performance data"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/rails")
        if response.status_code == 200:
            return response.json().get("rails", [])
        return []
    except:
        return []

def process_payment(payment_data):
    """Process a payment"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/payment/process",
            json=payment_data
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("detail", "Unknown error")
    except Exception as e:
        return None, str(e)

def reset_metrics():
    """Reset session metrics"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/metrics/reset")
        return response.status_code == 200
    except:
        return False

def main():
    """Main application"""
    
    # Header
    st.title("💳 Payment Processing Orchestrator")
    st.markdown("### AI-Powered Payment Routing with 5-Layer Architecture")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API Server is not running! Please start the API server first: `python api_server.py`")
        st.stop()
    
    st.success("✅ Connected to API Server")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.radio(
            "Select Page",
            ["Process Payment", "Real-Time Logs", "Session Metrics", "Corridors & Rails", "Architecture"]
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("Quick Stats")
        metrics = get_session_metrics()
        if metrics:
            st.metric("Total Payments", metrics["total_payments"])
            st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
            st.metric("Avg Processing", f"{metrics['avg_processing_time']:.2f}s")
        
        st.markdown("---")
        
        if st.button("🔄 Reset Session", type="secondary"):
            if reset_metrics():
                st.success("Session reset successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to reset session")
    
    # Main content
    if page == "Process Payment":
        show_payment_page()
    elif page == "Real-Time Logs":
        show_logs_page()
    elif page == "Session Metrics":
        show_metrics_page()
    elif page == "Corridors & Rails":
        show_corridors_rails_page()
    elif page == "Architecture":
        show_architecture_page()

def show_payment_page():
    """Payment processing page with auto-refresh"""
    st.header("💰 Process New Payment")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Standard Payment", "📋 Quick Templates", "📜 Recent Payments"])
    
    with tab1:
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sender Information")
                sender_name = st.text_input("Sender Name", value="Standard Bank of South Africa")
                sender_country = st.selectbox("Sender Country", ["ZA", "US", "GB", "DE", "BW"], index=0)
                currency_from = st.selectbox("From Currency", ["ZAR", "USD", "GBP", "EUR"], index=0)
            
            with col2:
                st.subheader("Receiver Information")
                receiver_name = st.text_input("Receiver Name", value="Global Trade Partners Inc")
                receiver_country = st.selectbox("Receiver Country", ["US", "GB", "ZA", "DE", "BW"], index=0)
                currency_to = st.selectbox("To Currency", ["USD", "GBP", "ZAR", "EUR"], index=0)
            
            st.subheader("Payment Details")
            col3, col4 = st.columns(2)
            
            with col3:
                amount = st.number_input("Amount", min_value=1.0, value=50000.0, step=1000.0)
            
            with col4:
                payment_purpose = st.text_input(
                    "Payment Purpose",
                    value="Trade settlement - imported goods"
                )
            
            submitted = st.form_submit_button("🚀 Process Payment", type="primary", use_container_width=True)
            
            if submitted:
                # Validate inputs
                if not sender_name or not receiver_name or not payment_purpose:
                    st.error("Please fill in all required fields")
                else:
                    # Prepare payment data
                    payment_data = {
                        "amount": amount,
                        "currency_from": currency_from,
                        "currency_to": currency_to,
                        "sender_country": sender_country,
                        "receiver_country": receiver_country,
                        "payment_purpose": payment_purpose,
                        "sender_name": sender_name,
                        "receiver_name": receiver_name
                    }
                    # Add to payment form:
                    st.subheader("🤖 AI Routing Preference")
                    routing_preference = st.radio(
                        "Select priority:",
                        ["fastest", "cheapest"],
                        horizontal=True
                    )
                    # Add to payment_data:
                    payment_data["routing_preference"] = routing_preference
    
                    # Create placeholders for real-time updates
                    status_container = st.empty()
                    logs_container = st.empty()
                    
                    with status_container:
                        st.info("🔄 Processing payment through 5-agent orchestrator...")
                    
                    # Process payment
                    result, error = process_payment(payment_data)
                    
                    if error:
                        # Handle error
                        status_container.empty()
                        st.error(f"❌ Payment Processing Failed")
                        st.error(f"Error: {error}")
                        
                        # Show error logs if available
                        if isinstance(error, dict) and 'logs' in error:
                            with st.expander("📜 View Error Logs", expanded=True):
                                for log in error['logs']:
                                    level = log.get('level', 'INFO')
                                    msg = log.get('message', '')
                                    if level == "ERROR":
                                        st.error(f"🔴 {msg}")
                                    elif level == "WARNING":
                                        st.warning(f"🟡 {msg}")
                                    else:
                                        st.text(f"   {msg}")
                    else:
                        # Success - clear status
                        status_container.empty()
                        
                        # Show success message
                        st.success(f"✅ Payment Processed Successfully!")
                        st.balloons()
                        
                        # Payment summary box
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>💳 Payment Complete</h3>
                            <p><strong>Payment ID:</strong> {result['payment_id']}</p>
                            <p><strong>Status:</strong> {result['status']}</p>
                            <p><strong>Selected Rail:</strong> {result['selected_rail']}</p>
                            <p><strong>Backup Rail:</strong> {result['backup_rail']}</p>
                            <p><strong>Processing Time:</strong> {result['total_processing_time']:.2f}s</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Processing details in columns
                        st.subheader("📊 Processing Details")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Compliance", result['compliance_status'],
                                     delta="Approved" if result['compliance_status'] == "APPROVED" else None)
                        with col2:
                            st.metric("Layer 4 Validation", result['layer4_validation'],
                                     delta="Passed" if result['layer4_validation'] == "APPROVED" else None)
                        with col3:
                            st.metric("Transaction Cost", f"${result['actual_cost']:.2f}")
                        with col4:
                            st.metric("Estimated Time", f"{result['actual_processing_time']:.1f}h")
                        
                        # Additional metrics
                        col5, col6, col7, col8 = st.columns(4)
                        
                        with col5:
                            st.metric("Risk Score", f"{result['risk_score']:.3f}")
                        with col6:
                            st.metric("Success", "✅ Yes" if result['success'] else "❌ No")
                        with col7:
                            st.metric("Reconciliation", result['reconciliation_status'])
                        with col8:
                            st.metric("State Key", result['state_key'][:12] + "...")
                        
                        # Processing Logs Viewer
                        st.subheader("📜 Processing Logs")
                        
                        if 'logs' in result and result['logs']:
                            # Create tabs for different log views
                            log_tab1, log_tab2 = st.tabs(["📋 Formatted View", "🔧 Raw Logs"])
                            
                            with log_tab1:
                                st.markdown("**Execution Timeline:**")
                                
                                for idx, log in enumerate(result['logs']):
                                    level = log.get('level', 'INFO')
                                    msg = log.get('message', '')
                                    timestamp = log.get('timestamp', '')
                                    
                                    # Skip empty messages
                                    if not msg.strip():
                                        continue
                                    
                                    # Color code by level
                                    if level == "ERROR":
                                        st.error(f"🔴 {msg}")
                                    elif level == "WARNING":
                                        st.warning(f"🟡 {msg}")
                                    elif "Agent" in msg or "Layer 4" in msg:
                                        st.info(f"🤖 {msg}")
                                    elif "✓ COMPLETED" in msg:
                                        st.success(f"✅ {msg}")
                                    elif "=" in msg:
                                        st.divider()
                                    else:
                                        st.text(f"   {msg}")
                            
                            with log_tab2:
                                # Show raw logs
                                log_text = "\n".join([
                                    f"[{log.get('timestamp', 'N/A')}] {log.get('level', 'INFO'):7s} | {log.get('message', '')}"
                                    for log in result['logs']
                                ])
                                st.code(log_text, language="log", line_numbers=True)
                        else:
                            st.info("No detailed logs available for this payment")
                        
                        # Complete JSON details in expander
                        with st.expander("🔍 View Complete Payment Details (JSON)"):
                            # Remove logs from JSON view to avoid duplication
                            result_copy = {k: v for k, v in result.items() if k != 'logs'}
                            st.json(result_copy)
                        
                        # Add new section after payment result:
                        with st.expander("🔍 PoC Validation Results"):
                            if "validation_result" in result:
                                validation = result["validation_result"]
                                st.metric("Compliance Status", validation["compliance_status"])
                                st.metric("Fraud Risk Score", f"{validation['fraud_risk_score']:.3f}")
                                st.metric("Sanctions Check", validation["sanctions_status"])
                                
                                if validation["violations"]:
                                    st.error("❌ Violations Found:")
                                    for v in validation["violations"]:
                                        st.text(f"- {v}")
                                
                                if validation["warnings"]:
                                    st.warning("⚠️ Warnings:")
                                    for w in validation["warnings"]:
                                        st.text(f"- {w}")

                        # Add new section:
                        with st.expander("🚂 Rail Selection Details"):
                            if "rail_selection" in result:
                                selection = result["rail_selection"]
                                st.metric("Selected Rail", selection["selected_rail"])
                                st.metric("Backup Rail", selection["backup_rail"])
                                st.text(f"Reason: {selection['reason']}")
                                st.metric("Estimated Cost", f"${selection['estimated_cost']:.2f}")
                                st.metric("Estimated Time", f"{selection['estimated_time_hours']:.2f}h")

                        # Add new section:
                        with st.expander("📧 Message Conversion"):
                            if "execution_details" in result and "conversion_details" in result["execution_details"]:
                                conv = result["execution_details"]["conversion_details"]
                                st.metric("Original Format", conv["from_format"])
                                st.metric("Converted Format", conv["to_format"])
                                st.metric("Conversion Time", f"{conv['conversion_time_ms']}ms")
    
    with tab2:
        show_templates()
    
    with tab3:
        show_recent_payments()

def show_templates():
    """Show quick payment templates"""
    st.subheader("📋 Quick Payment Templates")
    
    templates = {
        "Standard Cross-Border (ZA → US)": {
            "amount": 50000.0,
            "currency_from": "ZAR",
            "currency_to": "USD",
            "sender_country": "ZA",
            "receiver_country": "US",
            "sender_name": "Shoprite Holdings",
            "receiver_name": "American Import Export LLC",
            "payment_purpose": "Trade settlement - imported goods"
        },
        "High-Value Payment (ZA → GB)": {
            "amount": 250000.0,
            "currency_from": "ZAR",
            "currency_to": "GBP",
            "sender_country": "ZA",
            "receiver_country": "GB",
            "sender_name": "Discovery Limited",
            "receiver_name": "London Properties Ltd",
            "payment_purpose": "Property acquisition"
        },
        "Domestic Bulk (Payroll)": {
            "amount": 8500.0,
            "currency_from": "ZAR",
            "currency_to": "ZAR",
            "sender_country": "ZA",
            "receiver_country": "ZA",
            "sender_name": "MTN Group",
            "receiver_name": "Employee Collective Account",
            "payment_purpose": "Monthly payroll - employee salaries"
        },
        "Regional SADC (ZA → BW)": {
            "amount": 35000.0,
            "currency_from": "ZAR",
            "currency_to": "USD",
            "sender_country": "ZA",
            "receiver_country": "BW",
            "sender_name": "Anglo American Platinum",
            "receiver_name": "Botswana Mining Equipment Corp",
            "payment_purpose": "Regional trade - mining equipment"
        }
    }
    
    for template_name, template_data in templates.items():
        with st.expander(template_name):
            st.json(template_data)
            if st.button(f"Use {template_name}", key=template_name):
                with st.spinner("Processing..."):
                    result, error = process_payment(template_data)
                
                if error:
                    st.error(f"Failed: {error}")
                else:
                    st.success(f"✅ Payment {result['payment_id']} processed!")
                    st.metric("Status", result['status'])
                    st.metric("Rail", result['selected_rail'])
                    st.metric("Cost", f"${result['actual_cost']:.2f}")
                    
                    with st.expander("View Details"):
                        st.json(result)

def show_recent_payments():
    """Show recent payments"""
    st.subheader("📜 Session Payments")
    metrics = get_session_metrics()
    if metrics and metrics["total_payments"] > 0:
        st.info(f"Total payments processed in this session: {metrics['total_payments']}")
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    else:
        st.info("No payments processed yet in this session")

def show_logs_page():
    """Real-time logs page with auto-refresh"""
    st.header("📜 Real-Time Processing Logs")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("Logs auto-refresh every 2 seconds. Process a payment to see live execution!")
    
    with col2:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            if clear_logs():
                st.success("Logs cleared!")
                time.sleep(0.5)
                st.rerun()
    
    # Get logs
    logs_data = get_logs(last_n=200)
    
    if logs_data and logs_data['logs']:
        st.markdown(f"**Total Logs:** {logs_data['total_logs']} | **Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Display logs in a code block
        log_text = "\n".join(logs_data['logs'])
        
        st.markdown("""
        <div class="log-container">
        <pre>{}</pre>
        </div>
        """.format(log_text), unsafe_allow_html=True)
        
        # Auto-refresh every 2 seconds
        time.sleep(2)
        st.rerun()
    else:
        st.warning("No logs available. Process a payment to see execution logs!")

def show_metrics_page():
    """Session metrics dashboard"""
    st.header("📊 Session Metrics Dashboard")
    
    metrics = get_session_metrics()
    
    if not metrics or metrics["total_payments"] == 0:
        st.info("No payments processed yet. Process some payments to see metrics!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Payments", metrics["total_payments"], delta=metrics["successful"])
    
    with col2:
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    
    with col3:
        st.metric("Successful", metrics["successful"], delta=f"-{metrics['failed']} failed" if metrics['failed'] > 0 else "All successful")
    
    with col4:
        st.metric("Avg Processing", f"{metrics['avg_processing_time']:.2f}s")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Success/Failure Distribution")
        success_data = pd.DataFrame({
            "Status": ["Successful", "Failed"],
            "Count": [metrics["successful"], metrics["failed"]]
        })
        fig = px.pie(success_data, values="Count", names="Status", 
                    color="Status",
                    color_discrete_map={"Successful": "#28a745", "Failed": "#dc3545"})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚂 Payment Rails Usage")
        if metrics["rails_used"]:
            rails_data = pd.DataFrame([
                {"Rail": rail, "Count": count}
                for rail, count in metrics["rails_used"].items()
            ])
            fig = px.bar(rails_data, x="Rail", y="Count", color="Rail",
                        title="Distribution of Payments Across Rails")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rail usage data available")
    
    # Compliance stats
    st.subheader("🛡️ Compliance Statistics")
    comp_stats = metrics["compliance_stats"]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Approved", comp_stats["approved"])
    with col2:
        st.metric("⚠️ On Hold", comp_stats["hold"])
    with col3:
        st.metric("❌ Rejected", comp_stats["rejected"])
    
    # Layer 4 stats
    st.subheader("🔄 Layer 4 Integration Metrics")
    layer4_stats = metrics["layer4_stats"]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Validations", int(layer4_stats["total_validations"]))
    with col2:
        st.metric("Validation Failures", int(layer4_stats["failures"]))
    with col3:
        st.metric("Success Rate", f"{layer4_stats['success_rate']:.1f}%")
    
    # Session info
    st.markdown("---")
    st.subheader("📅 Session Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Session ID: {metrics['session_id']}")
        st.text(f"Start Time: {metrics['start_time']}")
    with col2:
        st.text(f"Duration: {metrics['duration_seconds']:.1f}s")

def show_corridors_rails_page():
    """Corridors and rails information"""
    st.header("🌍 Payment Corridors & Rails")
    
    tab1, tab2 = st.tabs(["🌐 Corridors", "🚂 Rails"])
    
    with tab1:
        st.subheader("Available Payment Corridors")
        corridors = get_corridors()
        
        if corridors:
            for corridor in corridors:
                with st.expander(f"📍 {corridor['corridor']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Compliance Level:** {corridor['compliance_level']}")
                        st.markdown(f"**Avg Processing:** {corridor['avg_processing_hours']} hours")
                        st.markdown(f"**Daily Limit:** ${corridor['daily_volume_limit']:,.0f}")
                    
                    with col2:
                        st.markdown("**Available Rails:**")
                        for rail in corridor['available_rails']:
                            st.markdown(f"- {rail}")
                        
                        st.markdown("**Regulatory Requirements:**")
                        for req in corridor.get('regulatory_requirements', []):
                            st.markdown(f"- {req}")
        else:
            st.info("No corridor data available")
    
    with tab2:
        st.subheader("Payment Rail Performance")
        rails = get_rails()
        
        if rails:
            rails_df = pd.DataFrame(rails)
            st.dataframe(
                rails_df,
                column_config={
                    "rail": "Rail Name",
                    "success_rate": st.column_config.ProgressColumn(
                        "Success Rate",
                        format="%.1f%%",
                        min_value=0,
                        max_value=1
                    ),
                    "avg_processing_time_hours": "Avg Time (hours)",
                    "avg_cost_usd": st.column_config.NumberColumn(
                        "Avg Cost",
                        format="$%.2f"
                    ),
                    "availability": st.column_config.ProgressColumn(
                        "Availability",
                        format="%.1f%%",
                        min_value=0,
                        max_value=1
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(rails_df, x="rail", y="success_rate",
                           title="Success Rate by Rail",
                           labels={"success_rate": "Success Rate", "rail": "Rail"})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(rails_df, x="avg_cost_usd", y="avg_processing_time_hours",
                               size="last_24h_volume", color="rail",
                               title="Cost vs Processing Time",
                               labels={
                                   "avg_cost_usd": "Average Cost (USD)",
                                   "avg_processing_time_hours": "Processing Time (hours)"
                               })
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rail performance data available")

def show_architecture_page():
    """Architecture overview"""
    st.header("🏗️ 5-Layer Architecture")
    
    st.markdown("""
    ## System Architecture Overview
    
    The Payment Processing Orchestrator uses a sophisticated 5-layer architecture
    with AI-powered routing and bidirectional Layer 4 integration.
    """)
    
    st.markdown("""
    ### Layer 1: Order Processing
    - BOLSA/AR, BOL Plus, Trade Apps, Mobile Apps
    - Canonical transformation layer
    
    ### Layer 2: VolPay (Internal Router)
    - **TWO-WAY INTEGRATION** with AI Orchestrator
    - Payment selector and router
    
    ### Layer 3: Agentic AI Orchestrator (Self-Hosted)
    - **Agent 1: Context Collector** - FX rates, corridors, performance metrics
    - **Agent 2: Policy Reasoner** - Ollama LLM for compliance validation
    - **Agent 3: Optimizer** - TensorFlow-based route selection
    - **Agent 4: Execution** - Message formatting and rail execution
    - **Agent 5: Feedback** - Continuous learning and improvement
    
    ### Layer 4: Payment Processing & Backoffice Systems
    - **BIDIRECTIONAL COMMUNICATION**
    - **Payment Processing:** PayEx, ICM, BOLPES, Infinity, CIMS
    - **Backoffice:** T24, Finacle, SAP, EE
    - Pre-execution validation & post-execution updates
    
    ### Layer 5: Payment Rails & Settlement
    - SWIFT_GPI, TAG, BANKSERV, NAMPAY, Settlement Networks
    
    ### Parallel: Logging & Monitoring
    - CIMS BAW-DD (transaction monitoring)
    - Firecosft (AML/sanctions)
    - AMS (audit logging)
    """)
    
    st.markdown("---")
    
    st.subheader("🎯 Key Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Operational Benefits:**
        - ✅ 25-40% latency reduction
        - ✅ 10-15% cost savings
        - ✅ 98%+ SLA compliance
        - ✅ 30% fewer manual exceptions
        - ✅ 50% faster reconciliation
        """)
    
    with col2:
        st.markdown("""
        **Technical Benefits:**
        - ✅ Complete data sovereignty
        - ✅ Real-time state management
        - ✅ ML-based optimization
        - ✅ Automatic failover
        - ✅ Continuous learning
        """)

if __name__ == "__main__":
    main()
