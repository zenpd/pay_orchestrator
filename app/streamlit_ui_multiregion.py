"""
Streamlit UI - Multi-Region Payment Orchestrator
Region selector with dynamic payment types and rails
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
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Payment Orchestrator - Multi-Region",
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
    .rail-fedwire { background-color: #1976D2; color: white; }
    .rail-ach { background-color: #0D47A1; color: white; }
    .rail-rtp { background-color: #00897B; color: white; }
    .rail-fps { background-color: #E91E63; color: white; }
    .rail-bacs { background-color: #673AB7; color: white; }
    .rail-chaps { background-color: #C2185B; color: white; }
    .rail-sepa { background-color: #0277BD; color: white; }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
    }
    .region-selector {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# REGION CONFIGURATIONS
# ============================================================

REGION_INFO = {
    "ZA": {
        "name": "🇿🇦 South Africa",
        "currency": "ZAR",
        "color": "#FFC107"
    },
    "US": {
        "name": "🇺🇸 United States",
        "currency": "USD",
        "color": "#1976D2"
    },
    "GB": {
        "name": "🇬🇧 United Kingdom",
        "currency": "GBP",
        "color": "#D32F2F"
    },
    "EU": {
        "name": "🇪🇺 Europe",
        "currency": "EUR",
        "color": "#388E3C"
    }
}

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "region" not in st.session_state:
    st.session_state.region = "ZA"  # Default region
if "payment_type" not in st.session_state:
    st.session_state.payment_type = None
if "logs" not in st.session_state:
    st.session_state.logs = []

# ============================================================
# HEADER
# ============================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 💳 Payment Orchestrator - Multi-Region")
    st.markdown("*Production-Grade Payment Processing with AI-Driven Rail Selection*")

with col2:
    st.markdown("### Region Selector")
    selected_region = st.selectbox(
        "Choose your region:",
        options=list(REGION_INFO.keys()),
        format_func=lambda x: REGION_INFO[x]["name"],
        key="region_selector"
    )
    st.session_state.region = selected_region

# Display selected region info
region_info = REGION_INFO[st.session_state.region]
st.markdown(f"""
<div class='region-selector'>
    <h3>Selected Region: {region_info['name']}</h3>
    <p><strong>Currency:</strong> {region_info['currency']}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Process Payment",
    "📊 Available Rails",
    "📈 Metrics",
    "📋 Logs"
])

# ============================================================
# TAB 1: PROCESS PAYMENT
# ============================================================

with tab1:
    st.subheader(f"Process Payment - {region_info['name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Payment Details")
        
        # Get payment types for selected region dynamically
        payment_types = {
            "ZA": {
                "Cross-Border Payment": {"description": "International payments with MT→MX conversion", "example": 50000},
                "Domestic Bulk Payment": {"description": "High-volume batch payments (EOD)", "example": 500000},
                "Domestic Instant": {"description": "Real-time small-value payments", "example": 5000},
                "Domestic Scheduled": {"description": "Scheduled domestic payments", "example": 15000},
                "SADC Regional": {"description": "SADC corridor payments", "example": 35000}
            },
            "US": {
                "Domestic Wire Transfer": {"description": "Fast same-day wire transfers", "example": 25000},
                "Domestic ACH (Bulk)": {"description": "Cost-effective bulk transfers (2-3 days)", "example": 100000},
                "Domestic Real-Time Payment": {"description": "Instant money movement (RTP)", "example": 50000},
                "International Wire": {"description": "Outbound international transfers", "example": 75000},
                "Inbound International": {"description": "Incoming international transfers", "example": 50000}
            },
            "GB": {
                "Faster Payment": {"description": "Faster Payments Service (same day)", "example": 30000},
                "BACS Transfer": {"description": "BACS bulk payments (3-5 days)", "example": 150000},
                "Real-Time Payment": {"description": "Faster Payments instant transfers", "example": 100000},
                "Outbound International": {"description": "International transfers from UK", "example": 50000},
                "Inbound International": {"description": "Receive international transfers", "example": 75000}
            },
            "EU": {
                "SEPA Transfer": {"description": "Single Euro Payment Area (1-2 days)", "example": 40000},
                "SEPA Instant": {"description": "SEPA Instant Credit Transfer (10 seconds)", "example": 100000},
                "SEPA Bulk": {"description": "SEPA batch processing", "example": 500000},
                "Outbound International": {"description": "Non-EU international transfers", "example": 75000},
                "Inbound International": {"description": "Receive from non-EU countries", "example": 50000}
            }
        }
        
        region_payment_types = payment_types.get(st.session_state.region, {})
        selected_payment_type = st.selectbox(
            "Payment Type:",
            options=list(region_payment_types.keys()) if region_payment_types else [],
            help="Select the type of payment for this region"
        )
        
        if selected_payment_type and region_payment_types.get(selected_payment_type):
            payment_detail = region_payment_types[selected_payment_type]
            st.info(f"📌 {payment_detail['description']}")
            example_amount = payment_detail.get("example", 10000)
        else:
            example_amount = 10000
        
        amount = st.number_input(
            f"Amount ({region_info['currency']}):",
            min_value=0.0,
            value=float(example_amount),
            step=100.0
        )
        
        # Currency pair based on region and payment type
        if "International" in selected_payment_type or "Cross-Border" in selected_payment_type:
            col_a, col_b = st.columns(2)
            with col_a:
                from_currency = st.selectbox("From:", ["USD", "GBP", "EUR", "ZAR"])
            with col_b:
                to_currency = st.selectbox("To:", ["USD", "GBP", "EUR", "ZAR"])
        else:
            from_currency = region_info["currency"]
            to_currency = region_info["currency"]
            st.text_input("From Currency:", value=from_currency, disabled=True)
            st.text_input("To Currency:", value=to_currency, disabled=True)
        
        sender_account = st.text_input("Sender Account:", placeholder="Account number")
        receiver_account = st.text_input("Receiver Account:", placeholder="Receiver account number")
        
        # Optimization preference
        optimization = st.radio(
            "Route Optimization:",
            options=["Speed-Focused", "Cost-Focused", "Balanced"],
            horizontal=True
        )
    
    with col2:
        st.markdown("### Processing Options")
        
        # Risk tolerance
        risk_tolerance = st.select_slider(
            "Risk Tolerance:",
            options=["Very Low", "Low", "Medium", "High"],
            value="Medium"
        )
        
        # Compliance requirements
        aml_check = st.checkbox("AML Check", value=True)
        sanctions_check = st.checkbox("Sanctions Check", value=True)
        fraud_check = st.checkbox("Fraud Detection", value=True)
        
        st.markdown("### Summary")
        
        summary_data = {
            "Region": region_info["name"],
            "Payment Type": selected_payment_type if selected_payment_type else "N/A",
            "Amount": f"{amount:,.2f} {from_currency}",
            "Optimization": optimization,
            "Risk Level": risk_tolerance,
            "Compliance": "All Checks" if (aml_check and sanctions_check and fraud_check) else "Partial"
        }
        
        summary_df = pd.DataFrame(list(summary_data.items()), columns=["Field", "Value"])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Process Button
        if st.button("🚀 Process Payment", use_container_width=True, type="primary"):
            with st.spinner("Processing payment..."):
                try:
                    payload = {
                        "region": st.session_state.region,
                        "payment_type": selected_payment_type,
                        "amount": amount,
                        "sender_country": "ZA" if st.session_state.region == "ZA" else st.session_state.region,
                        "receiver_country": "ZA" if st.session_state.region == "ZA" else st.session_state.region,
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "sender_account": sender_account,
                        "receiver_account": receiver_account,
                        "optimization": optimization,
                        "risk_tolerance": risk_tolerance,
                        "compliance": {
                            "aml_check": aml_check,
                            "sanctions_check": sanctions_check,
                            "fraud_check": fraud_check
                        }
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/process-payment", json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Payment Processed Successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", result.get("status", "Unknown"))
                        with col2:
                            st.metric("Payment ID", result.get("payment_id", "N/A")[:8] + "...")
                        with col3:
                            st.metric("Selected Rail", result.get("selected_rail", "N/A"))
                        
                        # Display execution details
                        st.markdown("### Execution Details")
                        execution_details = {
                            "Layer": result.get("execution_layer", "Full Pipeline"),
                            "Processing Time": f"{result.get('processing_time_ms', 0)}ms",
                            "Compliance Status": result.get("compliance_status", "Pending"),
                            "Route Score": f"{result.get('route_score', 0):.2f}",
                            "Cost": f"${result.get('estimated_cost', 0):.2f}"
                        }
                        
                        exec_df = pd.DataFrame(list(execution_details.items()), columns=["Item", "Value"])
                        st.dataframe(exec_df, use_container_width=True, hide_index=True)
                        
                        # Rails considered
                        if "rails_considered" in result:
                            st.markdown("### Rails Considered")
                            rails_data = result["rails_considered"]
                            rails_df = pd.DataFrame(rails_data).head(5)
                            st.dataframe(rails_df, use_container_width=True, hide_index=True)
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")

# ============================================================
# TAB 2: AVAILABLE RAILS
# ============================================================

with tab2:
    st.subheader(f"Available Payment Rails - {region_info['name']}")
    
    # Define rails for each region
    rails_info = {
        "ZA": {
            "SWIFT_GPI": {"type": "Cross-Border Express", "speed": "4.2h", "cost": "$28.50", "availability": "99.5%"},
            "SWIFT_TRADITIONAL": {"type": "Cross-Border Standard", "speed": "24h", "cost": "$22.00", "availability": "98.5%"},
            "PayShap_INSTANT": {"type": "Domestic Instant", "speed": "3.6s", "cost": "$0.25", "availability": "99.9%"},
            "PayShap_SCHEDULED": {"type": "Domestic Batched", "speed": "4h", "cost": "$0.15", "availability": "99.8%"},
            "RTGS_BULK": {"type": "Domestic Batch", "speed": "1h", "cost": "$25.00", "availability": "99.9%"}
        },
        "US": {
            "FedWire": {"type": "Domestic Express", "speed": "30min", "cost": "$15.00", "availability": "99.99%"},
            "RTP": {"type": "Real-Time Payment", "speed": "Instant", "cost": "$0.50", "availability": "99.7%"},
            "ACH_Express": {"type": "Domestic Fast", "speed": "Same Day", "cost": "$1.50", "availability": "99.8%"},
            "ACH_Standard": {"type": "Domestic Batch", "speed": "2-3 days", "cost": "$0.25", "availability": "99.9%"},
            "SWIFT_GPI": {"type": "International Express", "speed": "2-4h", "cost": "$30.00", "availability": "99.5%"}
        },
        "GB": {
            "FPS": {"type": "Faster Payment", "speed": "30min", "cost": "$2.50", "availability": "99.8%"},
            "CHAPS": {"type": "High-Value Same-Day", "speed": "Same Day", "cost": "$12.00", "availability": "99.99%"},
            "FPS_INSTANT": {"type": "Instant Payment", "speed": "Instant", "cost": "$1.00", "availability": "99.7%"},
            "BACS": {"type": "Bulk Transfer", "speed": "3-5 days", "cost": "$0.15", "availability": "99.99%"},
            "SWIFT_GPI": {"type": "International Express", "speed": "2-4h", "cost": "$28.00", "availability": "99.5%"}
        },
        "EU": {
            "SEPA_INST": {"type": "SEPA Instant", "speed": "10s", "cost": "$2.50", "availability": "99.8%"},
            "SEPA_CT": {"type": "SEPA Transfer", "speed": "1-2 days", "cost": "$1.50", "availability": "99.99%"},
            "TARGET2": {"type": "High-Value Real-Time", "speed": "Real-time", "cost": "$20.00", "availability": "99.99%"},
            "SEPA_Batch": {"type": "Bulk Processing", "speed": "1-2 days", "cost": "$0.20", "availability": "99.99%"},
            "SWIFT_GPI": {"type": "International Express", "speed": "2-4h", "cost": "$32.00", "availability": "99.5%"}
        }
    }
    
    region_rails = rails_info.get(st.session_state.region, {})
    
    if region_rails:
        # Create rail cards
        cols = st.columns(len(region_rails))
        
        for idx, (rail_name, rail_details) in enumerate(region_rails.items()):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
                    <h4>{rail_name}</h4>
                    <p><strong>Type:</strong> {rail_details['type']}</p>
                    <p><strong>Speed:</strong> {rail_details['speed']}</p>
                    <p><strong>Cost:</strong> {rail_details['cost']}</p>
                    <p><strong>Availability:</strong> {rail_details['availability']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No rails information available for this region")

# ============================================================
# TAB 3: METRICS
# ============================================================

with tab3:
    st.subheader(f"Performance Metrics - {region_info['name']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Transactions Today", "1,234", "+12%")
    with col2:
        st.metric("Success Rate", "99.2%", "+0.3%")
    with col3:
        st.metric("Avg Processing Time", "2.3s", "-0.5s")
    with col4:
        st.metric("Cost Saved", "$4,521", "+$340")
    
    # Charts
    st.markdown("### Rail Usage Distribution")
    
    rail_usage = {
        "ZA": {"SWIFT_GPI": 35, "PayShap_INSTANT": 28, "RTGS_BULK": 22, "PayShap_SCHEDULED": 10, "SADC_PAY": 5},
        "US": {"FedWire": 30, "RTP": 25, "ACH_Express": 20, "ACH_Standard": 18, "SWIFT_GPI": 7},
        "GB": {"FPS": 32, "CHAPS": 18, "FPS_INSTANT": 25, "BACS": 20, "SWIFT_GPI": 5},
        "EU": {"SEPA_INST": 28, "SEPA_CT": 32, "TARGET2": 15, "SEPA_Batch": 18, "SWIFT_GPI": 7}
    }
    
    region_usage = rail_usage.get(st.session_state.region, {})
    if region_usage:
        usage_df = pd.DataFrame(list(region_usage.items()), columns=["Rail", "Usage %"])
        st.bar_chart(usage_df.set_index("Rail"))

# ============================================================
# TAB 4: LOGS
# ============================================================

with tab4:
    st.subheader(f"Processing Logs - {region_info['name']}")
    
    if st.session_state.logs:
        logs_df = pd.DataFrame(st.session_state.logs)
        st.dataframe(logs_df, use_container_width=True, hide_index=True)
    else:
        st.info("No logs yet. Process a payment to see logs here.")
    
    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.success("Logs cleared!")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>🏦 Payment Orchestrator v2.0 - Multi-Region Support</p>
    <p>Powered by FastAPI, LangGraph, and AI-Driven Optimization</p>
</div>
""", unsafe_allow_html=True)
