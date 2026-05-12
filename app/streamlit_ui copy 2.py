"""
Streamlit UI - Payment Processing Orchestrator PoC
With rail selection dropdowns for SWIFT, PayShap, RTGS demos
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# ============================================================
# STREAMLIT PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Payment Orchestrator PoC",
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
    .rail-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8em;
        margin: 2px;
        display: inline-block;
    }
    .rail-swift { background-color: #4CAF50; color: white; }
    .rail-payshap { background-color: #2196F3; color: white; }
    .rail-rtgs { background-color: #FF9800; color: white; }
    .rail-sadc { background-color: #9C27B0; color: white; }
    .rail-partner { background-color: #607D8B; color: white; }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_rails():
    """Get all rails for dropdown"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/rails")
        if response.status_code == 200:
            return response.json().get("rails", [])
        return []
    except:
        return []

def get_corridors():
    """Get corridors"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/corridors")
        if response.status_code == 200:
            return response.json().get("corridors", [])
        return []
    except:
        return []

def process_payment(payment_data):
    """Process a payment"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/payment/process", json=payment_data)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("detail", "Unknown error")
    except Exception as e:
        return None, str(e)

def get_session_metrics():
    """Get metrics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/metrics/session")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_logs():
    """Get logs"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/logs", params={"last_n": 100})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def clear_logs():
    """Clear logs"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/logs/clear")
        return response.status_code == 200
    except:
        return False

def reset_metrics():
    """Reset metrics"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/metrics/reset")
        return response.status_code == 200
    except:
        return False

def get_rail_badge(rail_name):
    """Get colored badge for rail"""
    if "SWIFT" in rail_name:
        return f'<span class="rail-badge rail-swift">{rail_name}</span>'
    elif "PayShap" in rail_name:
        return f'<span class="rail-badge rail-payshap">{rail_name}</span>'
    elif "RTGS" in rail_name:
        return f'<span class="rail-badge rail-rtgs">{rail_name}</span>'
    elif "SADC" in rail_name:
        return f'<span class="rail-badge rail-sadc">{rail_name}</span>'
    else:
        return f'<span class="rail-badge rail-partner">{rail_name}</span>'

# ============================================================
# MAIN APP
# ============================================================

def main():
    """Main application"""
    
    # Header
    st.title("💳 Payment Orchestrator PoC")
    st.markdown("### AI-Powered Routing with Left-Shifted Validations")
    
    # Check API
    if not check_api_health():
        st.error("⚠️ API Server is not running! Start it with: `python api_server.py`")
        st.stop()
    
    st.success("✅ Connected to API Server")
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("📊 Demo Controls")
        
        # Rail Selection Dropdown (PRIMARY FILTER)
        st.subheader("🚂 Select Rail for Demo")
        rails = get_rails()
        rail_names = [r["rail"] for r in rails] if rails else []
        
        # Add "Auto (AI Selection)" option
        rail_options = ["Auto (AI Selection)"] + rail_names
        
        selected_rail_demo = st.selectbox(
            "Choose rail to demo:",
            rail_options,
            help="Select a specific rail or let AI choose automatically"
        )
        
        # Corridor Filter
        st.subheader("🌍 Corridor Filter")
        corridors = get_corridors()
        corridor_names = [c["corridor"] for c in corridors] if corridors else []
        
        selected_corridor = st.selectbox(
            "Filter by corridor:",
            ["All"] + corridor_names,
            help="Filter payments by country corridor"
        )
        
        # Routing Preference
        st.subheader("🤖 AI Preference")
        routing_preference = st.radio(
            "Customer priority:",
            ["fastest", "cheapest"],
            help="AI will prioritize speed or cost"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("📈 Session Stats")
        metrics = get_session_metrics()
        if metrics:
            st.metric("Total Payments", metrics.get("total_payments", 0))
            st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1%}")
            st.metric("Avg Time", f"{metrics.get('avg_processing_time', 0):.2f}s")
        
        # Reset Button
        if st.button("🔄 Reset Session", type="primary", use_container_width=True):
            if reset_metrics():
                st.success("Session reset!")
                time.sleep(1)
                st.rerun()
    
    # Main Tabs
    tabs = st.tabs(["💰 Process Payment", "📜 Live Logs", "📊 Metrics", "🌍 Corridors & Rails"])
    
    # Process Payment Tab
    with tabs[0]:
        show_payment_page(selected_rail_demo, selected_corridor, routing_preference)
    
    # Live Logs Tab
    with tabs[1]:
        show_logs_page()
    
    # Metrics Tab
    with tabs[2]:
        show_metrics_page()
    
    # Corridors & Rails Tab
    with tabs[3]:
        show_corridors_rails_page()

def show_payment_page(selected_rail_demo, selected_corridor, routing_preference):
    """Payment processing page with rail selection"""
    
    st.header("💰 Process New Payment")
    
    # Demo Mode Indicator
    if selected_rail_demo != "Auto (AI Selection)":
        st.info(f"🔧 Demo Mode: Forcing rail → {selected_rail_demo}")
    
    # Create form
    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sender Information")
            sender_name = st.text_input("Sender Name", value="Standard Bank of South Africa")
            sender_country = st.selectbox("Sender Country", ["ZA", "US", "GB", "BW"], index=0)
            currency_from = st.selectbox("From Currency", ["ZAR", "USD", "GBP", "EUR"], index=0)
        
        with col2:
            st.subheader("Receiver Information")
            receiver_name = st.text_input("Receiver Name", value="Global Trade Partners Inc")
            receiver_country = st.selectbox("Receiver Country", ["US", "GB", "ZA", "BW"], index=0)
            currency_to = st.selectbox("To Currency", ["USD", "GBP", "ZAR", "EUR"], index=0)
        
        st.subheader("Payment Details")
        col3, col4 = st.columns([2, 3])
        
        with col3:
            amount = st.number_input("Amount", min_value=1.0, value=50000.0, step=1000.0)
        
        with col4:
            payment_purpose = st.text_input("Purpose", value="Trade settlement - imported goods")
        
        # Show selected rail (if in demo mode)
        if selected_rail_demo != "Auto (AI Selection)":
            st.markdown("### 🚂 Selected Rail (Demo Override)")
            st.markdown(get_rail_badge(selected_rail_demo), unsafe_allow_html=True)
            
            # Show rail details
            rails = get_rails()
            rail_details = next((r for r in rails if r["rail"] == selected_rail_demo), None)
            if rail_details:
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("Success Rate", f"{rail_details.get('success_rate', 0):.1%}")
                with col_r2:
                    st.metric("Avg Cost", f"${rail_details.get('avg_cost_usd', 0):.2f}")
                with col_r3:
                    st.metric("Processing Time", f"{rail_details.get('avg_processing_time_hours', 0):.1f}h")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Process Payment", type="primary", use_container_width=True)
        
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0")
                return
            
            # Prepare payment data
            payment_data = {
                "amount": amount,
                "currency_from": currency_from,
                "currency_to": currency_to,
                "sender_country": sender_country,
                "receiver_country": receiver_country,
                "payment_purpose": payment_purpose,
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                "routing_preference": routing_preference
            }
            
            # Add demo rail override
            if selected_rail_demo != "Auto (AI Selection)":
                payment_data["demo_force_rail"] = selected_rail_demo
            
            # Process payment
            with st.spinner("🔄 Processing through 5-agent workflow..."):
                result, error = process_payment(payment_data)
            
            # Display results
            if error:
                st.error(f"❌ Payment Failed: {error}")
            else:
                display_payment_success(result)

def display_payment_success(result):
    """Display successful payment results"""
    
    st.success("✅ Payment Processed Successfully!")
    st.balloons()
    
    # Payment Summary
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 10px; background-color: #d4edda; border: 1px solid #c3e6cb;">
        <h3>💳 Payment Complete</h3>
        <p><strong>Payment ID:</strong> {result['payment_id']}</p>
        <p><strong>Status:</strong> {result['status']}</p>
        <p><strong>Selected Rail:</strong> {result['selected_rail']}</p>
        <p><strong>Processing Time:</strong> {result['total_processing_time']:.2f}s</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    st.subheader("📊 Processing Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Compliance Status", result['compliance_status'])
    with col2:
        st.metric("Layer 4", result['layer4_validation'])
    with col3:
        st.metric("Risk Score", f"{result['risk_score']:.3f}")
    with col4:
        st.metric("Cost", f"${result['actual_cost']:.2f}")
    
    # Rail Details
    st.subheader("🚂 Rail Selection")
    st.markdown(get_rail_badge(result['selected_rail']), unsafe_allow_html=True)
    st.markdown(get_rail_badge(result['backup_rail']), unsafe_allow_html=True)
    
    # Validation Results
    with st.expander("🔍 Pre-Validation Results", expanded=True):
        violations = result.get('validation_violations', [])
        warnings = result.get('validation_warnings', [])
        
        if violations:
            st.error("❌ Violations:")
            for v in violations:
                st.text(f"- {v}")
        
        if warnings:
            st.warning("⚠️ Warnings:")
            for w in warnings:
                st.text(f"- {w}")
        
        if not violations and not warnings:
            st.success("✅ All pre-validations passed")
        
        st.metric("Fraud Score", f"{result.get('fraud_check_score', 0):.3f}")
        st.metric("Sanctions", result.get('sanctions_check_status', 'UNKNOWN'))
    
    # Message Conversion
    with st.expander("📧 Message Format Conversion"):
        conv = result.get('message_conversion', {})
        if conv:
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("Original", conv.get('original', 'N/A'))
            with col_c2:
                st.metric("Converted", conv.get('converted', 'N/A'))
            with col_c3:
                st.metric("Time", f"{conv.get('conversion_time_ms', 0)}ms")
        
        # EFT Replacement Readiness
        if result.get('eft_replacement_ready'):
            st.success("✅ EFT Replacement Ready (2026-2027)")
        else:
            st.info("ℹ️ Already modern rail")

def show_logs_page():
    """Live logs page"""
    st.header("📜 Real-Time Processing Logs")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh", value=True)
    with col2:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            if clear_logs():
                st.success("Logs cleared!")
                time.sleep(0.5)
                st.rerun()
    
    logs_data = get_logs()
    if logs_data and logs_data['logs']:
        log_container = st.container()
        with log_container:
            for log in logs_data['logs'][-50:]:  # Last 50 lines
                st.code(log, language="log")
        
        if auto_refresh:
            time.sleep(2)
            st.rerun()
    else:
        st.info("No logs available. Process a payment to see live execution!")

def show_metrics_page():
    """Session metrics"""
    st.header("📊 PoC Session Analytics")
    
    metrics = get_session_metrics()
    if not metrics or metrics["total_payments"] == 0:
        st.info("No payments yet. Process some payments to see metrics!")
        return
    
    # Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Payments", metrics["total_payments"])
    with col2:
        st.metric("Success Rate", f"{metrics['success_rate']:.1%}")
    with col3:
        st.metric("Avg Processing", f"{metrics['avg_processing_time']:.2f}s")
    with col4:
        st.metric("EFT Ready Rails", sum(1 for r in get_rails() if r.get('eft_replacement_ready', False)))
    
    # Rail Usage
    st.subheader("🚂 Rail Distribution")
    if "rails_used" in metrics:
        rail_data = pd.DataFrame([
            {"Rail": rail, "Count": count}
            for rail, count in metrics["rails_used"].items()
        ])
        st.dataframe(rail_data, use_container_width=True)
    
    # Validation Stats
    st.subheader("🔍 Pre-Validation Stats")
    if metrics.get("total_payments", 0) > 0:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.metric("Violations Avg", f"{len(metrics.get('validation_violations', []))/metrics['total_payments']:.1f} per payment")
        with col_v2:
            st.metric("Warnings Avg", f"{len(metrics.get('validation_warnings', []))/metrics['total_payments']:.1f} per payment")

def show_corridors_rails_page():
    """Corridors and rails information with defensive column checking"""
    st.header("🌍 PoC Corridors & Rails")
    
    # Rails Table
    st.subheader("🚂 Payment Rails (PoC Scope)")
    rails = get_rails()
    
    if rails:
        # Convert to DataFrame
        rails_df = pd.DataFrame(rails)
        
        # SAFE: Add EFT replacement column (if it exists in data)
        if "eft_replacement_ready" in rails_df.columns:
            rails_df["EFT Ready"] = rails_df["eft_replacement_ready"].apply(
                lambda x: "✅ Yes" if x else "ℹ️ N/A"
            )
        else:
            # Add column with default values if missing
            rails_df["EFT Ready"] = "ℹ️ N/A"
        
        # SAFE: Build display columns dynamically
        # Start with columns we know exist
        display_cols = ["rail"]
        
        # Only add columns that actually exist in the DataFrame
        for col in ["type", "success_rate", "avg_cost_usd", 
                   "avg_processing_time_hours", "availability"]:
            if col in rails_df.columns:
                display_cols.append(col)
        
        # Add EFT Ready if we created it
        if "EFT Ready" in rails_df.columns:
            display_cols.append("EFT Ready")
        
        # Check if we have any columns to display besides 'rail'
        if len(display_cols) == 1:  # Only 'rail' column exists
            st.warning("No detailed rail data available. Loading minimal view...")
            st.dataframe(rails_df[display_cols], hide_index=True, use_container_width=True)
        else:
            # Display with column formatting
            st.dataframe(
                rails_df[display_cols],
                column_config={
                    "rail": "Rail Name",
                    "type": "Rail Type",
                    "success_rate": st.column_config.ProgressColumn(
                        "Success Rate", format="%.1f%%", min_value=0, max_value=1
                    ),
                    "avg_cost_usd": st.column_config.NumberColumn("Avg Cost", format="$%.2f"),
                    "avg_processing_time_hours": st.column_config.NumberColumn("Avg Time (h)", format="%.2f"),
                    "availability": st.column_config.ProgressColumn("Availability", format="%.1f%%", min_value=0, max_value=1),
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Show rail details (SAFE version)
        st.subheader("Rail Details")
        selected_rail_detail = st.selectbox("Select rail for details:", [r["rail"] for r in rails])
        
        rail_detail = next((r for r in rails if r["rail"] == selected_rail_detail), None)
        if rail_detail:
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Success Rate", f"{rail_detail.get('success_rate', 0):.1%}")
                st.metric("Daily Volume", f"{rail_detail.get('last_24h_volume', 0):,}")
            with col_r2:
                st.metric("Avg Cost", f"${rail_detail.get('avg_cost_usd', 0):.2f}")
                st.metric("Daily Failures", f"{rail_detail.get('last_24h_failures', 0)}")
            with col_r3:
                st.metric("Avg Time", f"{rail_detail.get('avg_processing_time_hours', 0):.1f}h")
                st.metric("Availability", f"{rail_detail.get('availability', 0):.1%}")
            
            # SAFE: Message Format & EFT Status
            st.markdown("---")
            col_rf1, col_rf2 = st.columns(2)
            with col_rf1:
                st.metric("Message Format", rail_detail.get("message_format", "UNKNOWN"))
            with col_rf2:
                # SAFE: Check if key exists
                eft_ready = rail_detail.get("eft_replacement_ready", False)
                if eft_ready:
                    st.success("✅ EFT Replacement Ready (2026-2027)")
                else:
                    st.info("ℹ️ Already modern rail")
    
    # Corridors
    st.markdown("---")
    st.subheader("🌐 Available Corridors")
    corridors = get_corridors()
    
    if corridors:
        for corridor in corridors:
            with st.expander(f"📍 {corridor['corridor']}"):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown(f"**Compliance Level:** {corridor['compliance_level']}")
                    st.markdown(f"**Avg Processing:** {corridor['avg_processing_hours']} hours")
                    st.markdown(f"**Daily Limit:** ${corridor['daily_volume_limit']:,.0f}")
                with col_c2:
                    st.markdown("**Available Rails:**")
                    for rail in corridor['available_rails']:
                        st.markdown(get_rail_badge(rail), unsafe_allow_html=True)

if __name__ == "__main__":
    main()