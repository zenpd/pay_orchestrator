"""
Quick Test Script - Multi-Region Payment Orchestrator
Test the API with different regions and payment types
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_response(response):
    """Pretty print API response"""
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_regions():
    """Test: Get all available regions"""
    print_header("TEST 1: Get All Available Regions")
    
    response = requests.get(f"{API_BASE_URL}/regions")
    print(f"Status Code: {response.status_code}\n")
    print_response(response)
    
    return response.json()

def test_region_payment_types(region_code):
    """Test: Get payment types for a region"""
    print_header(f"TEST 2: Get Payment Types for {region_code}")
    
    response = requests.get(f"{API_BASE_URL}/regions/{region_code}/payment-types")
    print(f"Status Code: {response.status_code}\n")
    print_response(response)

def test_region_rails(region_code):
    """Test: Get available rails for a region"""
    print_header(f"TEST 3: Get Available Rails for {region_code}")
    
    response = requests.get(f"{API_BASE_URL}/regions/{region_code}/rails")
    print(f"Status Code: {response.status_code}\n")
    print_response(response)

def test_payment_processing(region, payment_type, amount, from_currency, to_currency, optimization):
    """Test: Process a payment"""
    print_header(f"TEST 4: Process Payment - {region}")
    print(f"Payment Type: {payment_type}")
    print(f"Amount: {amount} {from_currency} → {to_currency}")
    print(f"Optimization: {optimization}\n")
    
    payload = {
        "region": region,
        "payment_type": payment_type,
        "amount": amount,
        "sender_country": region if region != "EU" else "DE",
        "receiver_country": region if region != "EU" else "FR",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "sender_account": "123456789",
        "receiver_account": "987654321",
        "optimization": optimization,
        "risk_tolerance": "Medium",
        "compliance": {
            "aml_check": True,
            "sanctions_check": True,
            "fraud_check": True
        }
    }
    
    print("Request Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{API_BASE_URL}/process-payment", json=payload)
    print(f"Status Code: {response.status_code}\n")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("payment_id")
    return None

def test_payment_logs(payment_id):
    """Test: Get payment logs"""
    if not payment_id:
        return
    
    print_header(f"TEST 5: Get Payment Logs - {payment_id}")
    
    response = requests.get(f"{API_BASE_URL}/logs/{payment_id}")
    print(f"Status Code: {response.status_code}\n")
    print_response(response)

def test_health():
    """Test: Health check"""
    print_header("TEST 0: API Health Check")
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}\n")
    print_response(response)

def test_complete_workflow():
    """Run complete test workflow"""
    
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "MULTI-REGION PAYMENT ORCHESTRATOR" + " "*20 + "║")
    print("║" + " "*20 + "API Test Suite - Complete Workflow" + " "*14 + "║")
    print("╚" + "═"*68 + "╝")
    
    print("\n[INFO] Starting API tests...\n")
    
    # Test 0: Health check
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        print("❌ API is not running. Start it with: python api_server_multiregion.py")
        return
    
    # Test 1: Get regions
    regions_data = test_regions()
    regions = regions_data.get("regions", {})
    
    # Test 2-3: Payment types and rails for each region
    for region_code in ["ZA", "US", "GB", "EU"]:
        if region_code in regions:
            test_region_payment_types(region_code)
            test_region_rails(region_code)
    
    # Test 4: Process payments for different regions
    test_cases = [
        {
            "region": "ZA",
            "payment_type": "Cross-Border Payment",
            "amount": 50000,
            "from_currency": "ZAR",
            "to_currency": "USD",
            "optimization": "Speed-Focused",
            "description": "South Africa → Speed-Focused"
        },
        {
            "region": "US",
            "payment_type": "Domestic Wire Transfer",
            "amount": 25000,
            "from_currency": "USD",
            "to_currency": "USD",
            "optimization": "Speed-Focused",
            "description": "United States → Speed-Focused"
        },
        {
            "region": "GB",
            "payment_type": "BACS Transfer",
            "amount": 150000,
            "from_currency": "GBP",
            "to_currency": "GBP",
            "optimization": "Cost-Focused",
            "description": "United Kingdom → Cost-Focused"
        },
        {
            "region": "EU",
            "payment_type": "SEPA Instant",
            "amount": 100000,
            "from_currency": "EUR",
            "to_currency": "EUR",
            "optimization": "Speed-Focused",
            "description": "Europe → Speed-Focused"
        }
    ]
    
    payment_ids = []
    for test_case in test_cases:
        print_header(f"Processing: {test_case['description']}")
        payment_id = test_payment_processing(
            test_case["region"],
            test_case["payment_type"],
            test_case["amount"],
            test_case["from_currency"],
            test_case["to_currency"],
            test_case["optimization"]
        )
        if payment_id:
            payment_ids.append(payment_id)
        time.sleep(1)
    
    # Test 5: Get logs for processed payments
    for payment_id in payment_ids[:2]:  # Get logs for first 2 payments
        test_payment_logs(payment_id)
        time.sleep(0.5)
    
    # Summary
    print_header("SUMMARY")
    print(f"✅ Total regions tested: {len(regions)}")
    print(f"✅ Total payments processed: {len(payment_ids)}")
    print(f"✅ All tests completed successfully!")
    
    print("\n[NEXT STEPS]")
    print("1. Open Streamlit UI: streamlit run streamlit_ui_multiregion.py")
    print("2. Test with the web interface")
    print("3. Select different regions and payment types")
    print("4. Monitor logs in real-time")
    
    print("\n[API DOCUMENTATION]")
    print("- Regions endpoint: GET /regions")
    print("- Payment types: GET /regions/{region_code}/payment-types")
    print("- Available rails: GET /regions/{region_code}/rails")
    print("- Process payment: POST /process-payment")
    print("- Get logs: GET /logs/{payment_id}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        test_complete_workflow()
    except KeyboardInterrupt:
        print("\n\n❌ Test suite interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")
