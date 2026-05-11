"""
Streamlit UI - Payment Orchestrator PoC (Enhanced)
Payment Type selection with multi-rail AI intelligence
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import random

# Configuration
API_BASE_URL = "http://localhost:8000"

# ============================================================
# PAYMENT TYPE DEFINITIONS (Enhanced with Multiple Rails)
# ============================================================

PAYMENT_TYPES = {
    "Cross-Border Payment": {
        "description": "International payments with MT→MX conversion",
        "corridor": "ZA_US",
        "rails": ["SWIFT_GPI", "NAMPAY", "PARTNER_NETWORK"],  # AI chooses based on speed/cost
        "default_currency": ("ZAR", "USD"),
        "example_amount": 50000.0,
        "typical_use": "High-value, standard international transfers"
    },
    "Domestic Bulk Payment": {
        "description": "High-volume batch payments (EOD processing)",
        "corridor": "ZA_ZA",
        "rails": ["RTGS_BULK", "BATCH_ACH", "SLOW_BATCH"],  # AI chooses based on volume/time
        "default_currency": ("ZAR", "ZAR"),
        "example_amount": 500000.0,
        "typical_use": "Payroll, supplier bulk payments"
    },
    "Domestic Non-Bulk (Instant)": {
        "description": "Real-time small-value payments",
        "corridor": "ZA_ZA",
        "rails": ["PayShap_INSTANT", "RTGS_REALTIME", "CARD_RAIL"],  # AI chooses fastest
        "default_currency": ("ZAR", "ZAR"),
        "example_amount": 5000.0,
        "typical_use": "P2P, small business urgent payments"
    },
    "Domestic Non-Bulk (Scheduled)": {
        "description": "Scheduled domestic payments (4-hour batches)",
        "corridor": "ZA_ZA",
        "rails": ["PayShap_SCHEDULED", "STANDING_ORDER", "BATCH_ACH"],  # AI chooses based on schedule
        "default_currency": ("ZAR", "ZAR"),
        "example_amount": 15000.0,
        "typical_use": "Recurring bills, scheduled transfers"
    },
    "SADC Regional Payment": {
        "description": "SADC corridor payments with regional compliance",
        "corridor": "ZA_BW",
        "rails": ["SADC_PAY", "SWIFT_GPI", "REGIONAL_PARTNER"],  # AI chooses based on cost/risk
        "default_currency": ("ZAR", "USD"),
        "example_amount": 35000.0,
        "typical_use": "Regional trade, cross-border business"
    }
}

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
    .rail-ach { background-color: #795548; color: white; }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_rails():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/rails")
        if response.status_code == 200:
            return response.json().get("rails", [])
        return []
    except:
        return []

def process_payment(payment_data):
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/payment/process", json=payment_data)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("detail", "Unknown error")
    except Exception as e:
        return None, str(e)

def get_session_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/metrics/session")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_logs():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/logs", params={"last_n": 100})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def clear_logs():
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/logs/clear")
        return response.status_code == 200
    except:
        return False

def reset_metrics():
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/metrics/reset")
        return response.status_code == 200
    except:
        return False

def get_rail_badge(rail_name):
    if "SWIFT" in rail_name:
        return f'<span class="rail-badge rail-swift">{rail_name}</span>'
    elif "PayShap" in rail_name:
        return f'<span class="rail-badge rail-payshap">{rail_name}</span>'
    elif "RTGS" in rail_name:
        return f'<span class="rail-badge rail-rtgs">{rail_name}</span>'
    elif "SADC" in rail_name:
        return f'<span class="rail-badge rail-sadc">{rail_name}</span>'
    elif "ACH" in rail_name:
        return f'<span class="rail-badge rail-ach">{rail_name}</span>'
    else:
        return f'<span class="rail-badge rail-partner">{rail_name}</span>'

def main():
    st.title("💳 Payment Orchestrator PoC")
    st.markdown("### AI-Powered Multi-Rail Selection Engine")
    
    if not check_api_health():
        st.error("⚠️ API Server is not running! Start it with: `python api_server.py`")
        st.stop()
    
    st.success("✅ Connected")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Demo Controls")
        
        st.subheader("Select Payment Type")
        payment_type = st.selectbox(
            "Choose payment scenario:",
            list(PAYMENT_TYPES.keys()),
            help="AI will evaluate multiple rails and select the optimal one"
        )
        
        config = PAYMENT_TYPES[payment_type]
        st.info(f"**{config['description']}**")
        st.caption(f"Typical use: {config['typical_use']}")
        
        st.markdown("**🚂 Available Rails for AI Evaluation:**")
        for rail in config["rails"]:
            st.markdown(get_rail_badge(rail), unsafe_allow_html=True)
        
        st.subheader("🤖 AI Customer Preference")
        routing_preference = st.radio(
            "Priority weighting:",
            ["fastest", "cheapest", "balanced"],
            help="AI will weight speed vs cost in its selection algorithm"
        )
        
        # Payment characteristics that influence AI
        st.subheader("📊 Payment Characteristics")
        urgency = st.slider("Urgency Level", 1, 10, 5, 
                           help="Higher urgency = faster rail preferred")
        risk_tolerance = st.slider("Risk Tolerance", 1, 10, 7,
                                  help="Higher tolerance = cheaper but riskier rails acceptable")
        
        st.markdown("---")
        
        st.subheader("📈 Session Stats")
        metrics = get_session_metrics()
        if metrics:
            st.metric("Total Payments", metrics.get("total_payments", 0))
            st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1%}")
            st.metric("Avg Time", f"{metrics.get('avg_processing_time', 0):.2f}s")
        
        if st.button("🔄 Reset Session", type="primary", use_container_width=True):
            if reset_metrics():
                st.success("Session reset!")
                time.sleep(1)
                st.rerun()
    
    # Main Tabs
    tabs = st.tabs(["💰 Process Payment", "📜 Live Logs", "📊 Metrics", "🌍 Rails Catalog"])
    
    with tabs[0]:
        show_payment_page(payment_type, routing_preference, urgency, risk_tolerance)
    
    with tabs[1]:
        show_logs_page()
    
    with tabs[2]:
        show_metrics_page()
    
    with tabs[3]:
        show_rails_catalog_page()

def show_payment_page(payment_type, routing_preference, urgency, risk_tolerance):
    st.header(f"💰 {payment_type}")
    
    config = PAYMENT_TYPES[payment_type]
    
    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sender Information")
            sender_name = st.text_input("Sender Name", value="Standard Bank of South Africa")
            sender_country = st.text_input("Sender Country", value=config["corridor"].split("_")[0], disabled=True)
            currency_from = st.text_input("From Currency", value=config["default_currency"][0], disabled=True)
        
        with col2:
            st.subheader("Receiver Information")
            receiver_name = st.text_input("Receiver Name", value="Global Trade Partners Inc")
            receiver_country = st.text_input("Receiver Country", value=config["corridor"].split("_")[1], disabled=True)
            currency_to = st.text_input("To Currency", value=config["default_currency"][1], disabled=True)
        
        st.subheader("Payment Details")
        col3, col4 = st.columns([2, 3])
        
        with col3:
            amount = st.number_input("Amount", min_value=1.0, value=float(config["example_amount"]), step=1000.0)
        
        with col4:
            payment_purpose = st.text_input("Purpose", value="Trade settlement - imported goods")
        
        st.markdown("### 🔍 AI Rail Selection Preview")
        st.info(f"Preference: **{routing_preference}** | Urgency: **{urgency}/10** | Risk Tolerance: **{risk_tolerance}/10**")
        
        submitted = st.form_submit_button("🚀 Process Payment with AI Analysis", type="primary", use_container_width=True)
        
        if submitted:
            payment_data = {
                "amount": amount,
                "currency_from": currency_from,
                "currency_to": currency_to,
                "sender_country": sender_country,
                "receiver_country": receiver_country,
                "payment_purpose": payment_purpose,
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                "routing_preference": routing_preference,
                "urgency": urgency,
                "risk_tolerance": risk_tolerance
            }
            
            with st.spinner("🤖 AI analyzing rails and selecting optimal path..."):
                result, error = process_payment(payment_data)
            
            if error:
                st.error(f"❌ Failed: {error}")
            else:
                display_payment_success(result, payment_type, config)

def display_payment_success(result, payment_type, config):
    st.success("✅ Payment Processed Successfully!")
    st.balloons()
    
    # Payment Summary Card
    st.markdown(f"""
    <div class="score-card">
        <h3>💳 Payment Complete</h3>
        <p><strong>Payment ID:</strong> {result['payment_id']}</p>
        <p><strong>Type:</strong> {payment_type}</p>
        <p><strong>Status:</strong> <span style="color:#4CAF50;">{result['status']}</span></p>
        <p><strong>AI-Selected Rail:</strong> {result['selected_rail']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Decision Reasoning
    with st.expander("🤖 AI Rail Selection Reasoning (Click to Expand)", expanded=True):
        if "selection_details" in result:
            details = result["selection_details"]
            
            st.subheader("🎯 Decision Summary")
            col_pref, col_method = st.columns(2)
            with col_pref:
                st.metric("Customer Preference", details['preference_applied'].title())
            with col_method:
                st.metric("Scoring Algorithm", details['scoring_method'])
            
            st.markdown("### 📊 Rail Scoring Breakdown")
            
            # Selected Rail Card
            st.markdown("#### ✅ Selected Rail")
            sel = details["selected"]
            st.markdown(get_rail_badge(sel["rail"]), unsafe_allow_html=True)
            
            col_score1, col_score2, col_score3 = st.columns(3)
            with col_score1:
                st.metric("Final Score", f"{sel['score']}/100", 
                         help="Weighted score based on preference and penalties")
            with col_score2:
                st.metric("Speed Score", f"{sel['attributes']['speed_score']}/100")
            with col_score3:
                st.metric("Cost Score", f"{sel['attributes']['cost_score']}/100")
            
            col_attr1, col_attr2, col_attr3 = st.columns(3)
            with col_attr1:
                st.metric("Capacity Check", "✅ PASS" if sel['attributes']['capacity_ok'] else "❌ FAIL")
            with col_attr2:
                st.metric("Risk Level", sel['attributes']['risk_level'])
            with col_attr3:
                st.metric("Regulatory", sel['attributes']['regulatory_overhead'])
            
            # Show all evaluated rails
            st.markdown("#### 📋 All Rails Evaluated")
            if "all_scored_rails" in details:
                comparison_data = []
                for s in details['all_scored_rails']:
                    comparison_data.append({
                        "Rail": s['rail'],
                        "Final Score": s['final_score'],
                        "Speed": s['speed_score'],
                        "Cost Efficiency": s['cost_score'],
                        "Capacity": "✅" if s['capacity_ok'] else "❌",
                        "Risk": s['risk_level'],
                        "Regulatory": s['regulatory_overhead'],
                        "AI Decision": "🥇 SELECTED" if s['rail'] == sel['rail'] else "❌"
                    })
                
                df = pd.DataFrame(comparison_data).sort_values("Final Score", ascending=False)
                st.dataframe(
                    df,
                    column_config={
                        "Final Score": st.column_config.ProgressColumn("Final Score", format="%d", min_value=0, max_value=100),
                        "Speed": st.column_config.NumberColumn("Speed"),
                        "Cost Efficiency": st.column_config.NumberColumn("Cost"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            # Why this rail won
            st.markdown("#### 🏆 Selection Justification")
            st.info(f"**Primary Reason:** {details.get('justification', 'AI scored this rail highest based on your preferences')}")
            
            # Runner-up comparison
            if details.get("runner_up"):
                ru = details["runner_up"]
                st.markdown("#### 🥈 Runner-Up Comparison")
                col_ru1, col_ru2 = st.columns(2)
                with col_ru1:
                    st.markdown(get_rail_badge(ru['rail']), unsafe_allow_html=True)
                    st.metric("Score", f"{ru['score']}/100")
                with col_ru2:
                    st.metric("Margin", f"-{ru['margin']} pts", 
                             delta="Worse", delta_color="inverse")
                    st.caption(f"Reason: {ru.get('reason', 'Lower weighted score')}")
    
    # Additional Details
    with st.expander("🔍 Pre-Validation & Compliance", expanded=False):
        st.metric("Fraud Check Score", f"{result.get('fraud_check_score', 0):.3f}")
        st.metric("Sanctions Status", result.get('sanctions_check_status', 'UNKNOWN'))
        violations = result.get('validation_violations', [])
        if violations:
            st.error("❌ Violations: " + ", ".join(violations))
        else:
            st.success("✅ All pre-validations passed")

def show_logs_page():
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
            st.code("\n".join(logs_data['logs'][-50:]), language="log")
        
        if auto_refresh:
            time.sleep(2)
            st.rerun()
    else:
        st.info("No logs available. Process a payment to see live execution!")

def show_metrics_page():
    st.header("📊 PoC Session Analytics")
    
    metrics = get_session_metrics()
    if not metrics or metrics["total_payments"] == 0:
        st.info("No payments yet. Process some payments to see metrics!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Payments", metrics["total_payments"])
    with col2:
        st.metric("Success Rate", f"{metrics['success_rate']:.1%}")
    with col3:
        st.metric("Avg Processing", f"{metrics['avg_processing_time']:.2f}s")
    with col4:
        st.metric("Total Volume", f"${metrics.get('total_volume', 0):,.0f}")
    
    # Rail usage distribution
    st.subheader("🚂 AI Rail Selection Distribution")
    rails_used = metrics.get('rails_used', {})
    if rails_used:
        df = pd.DataFrame([
            {"Rail": rail, "Selections": count}
            for rail, count in rails_used.items()
        ])
        st.bar_chart(df.set_index("Rail"))
    
    # Preference analysis
    st.subheader("🤖 Preference Analysis")
    pref_data = metrics.get('preference_analysis', {})
    if pref_data:
        col_pref1, col_pref2 = st.columns(2)
        with col_pref1:
            st.metric("Fastest Picks", pref_data.get('fastest', 0))
        with col_pref2:
            st.metric("Cheapest Picks", pref_data.get('cheapest', 0))

def show_rails_catalog_page():
    st.header("🚂 Rails Performance Catalog")
    
    rails = get_rails()
    if rails:
        for rail in rails:
            with st.expander(f"📡 {rail['rail']}"):
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("Type", rail.get("type", "N/A"))
                    st.metric("Success Rate", f"{rail.get('success_rate', 0):.1%}")
                with col_r2:
                    st.metric("Avg Cost", f"${rail.get('avg_cost_usd', 0):.2f}")
                    st.metric("Max Amount", f"${rail.get('max_amount', 0):,.0f}")
                with col_r3:
                    st.metric("Speed Score", f"{rail.get('speed_score', 0)}/100")
                    st.metric("Cost Score", f"{rail.get('cost_score', 0)}/100")
                
                # Attributes
                st.markdown("**Attributes:**")
                st.markdown(f"- Risk Level: `{rail.get('risk_level', 'N/A')}`")
                st.markdown(f"- Regulatory: `{rail.get('regulatory_overhead', 'N/A')}`")
                st.markdown(f"- Capacity: `{rail.get('capacity_per_hour', 0)} transactions/hour`")

if __name__ == "__main__":
    main()