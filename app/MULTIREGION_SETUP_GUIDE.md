# Multi-Region Payment Orchestrator Setup Guide

## 🌍 Overview

This enhanced version of the Payment Orchestrator now supports **4 major regions** with region-specific payment rails, currencies, and processing optimizations:

- 🇿🇦 **South Africa (ZA)** - PayShap, RTGS, SWIFT, SADC
- 🇺🇸 **United States (US)** - FedWire, ACH, RTP, CHIPS
- 🇬🇧 **United Kingdom (GB)** - FPS, BACS, CHAPS, SWIFT
- 🇪🇺 **Europe (EU)** - SEPA, TARGET2, SWIFT

## ✨ New Features

### 1. **Region Selector Dropdown**
   - Frontend: Easy region selection on the Streamlit UI
   - Dynamically loads payment types for selected region
   - Currency automatically adjusts to regional standard

### 2. **Region-Specific Payment Types**
   Each region has 5 payment scenarios tailored to local infrastructure:
   - **ZA**: Cross-Border, Domestic Bulk, Instant, Scheduled, SADC Regional
   - **US**: Domestic Wire, ACH Bulk, Real-Time (RTP), International Wire, Inbound
   - **GB**: Faster Payment, BACS, Real-Time, Outbound, Inbound International
   - **EU**: SEPA Transfer, SEPA Instant, SEPA Bulk, Outbound, Inbound

### 3. **Region-Specific Payment Rails**
   
   **South Africa:**
   - SWIFT_GPI: 4.2h, $28.50
   - SWIFT_TRADITIONAL: 24h, $22.00
   - PayShap_INSTANT: 3.6s, $0.25
   - PayShap_SCHEDULED: 4h, $0.15
   - RTGS_BULK: 1h, $25.00

   **United States:**
   - FedWire: 30min, $15.00
   - RTP (Real-Time Payment): Instant, $0.50
   - ACH_Express: Same Day, $1.50
   - ACH_Standard: 2-3 days, $0.25
   - SWIFT_GPI: 2-4h, $30.00

   **United Kingdom:**
   - FPS (Faster Payments): 30min, $2.50
   - CHAPS: Same Day, $12.00
   - FPS_INSTANT: Instant, $1.00
   - BACS: 3-5 days, $0.15
   - SWIFT_GPI: 2-4h, $28.00

   **Europe (SEPA):**
   - SEPA_INST: 10 seconds, $2.50
   - SEPA_CT: 1-2 days, $1.50
   - TARGET2: Real-time, $20.00
   - SEPA_Batch: 1-2 days, $0.20
   - SWIFT_GPI: 2-4h, $32.00

### 4. **AI-Driven Rail Selection**
   - Speed-Focused optimization
   - Cost-Focused optimization
   - Balanced optimization (default)
   - Risk tolerance awareness
   - Amount compatibility checking
   - Availability scoring

## 🚀 Quick Start

### Option 1: Single Terminal (Development)

```bash
# Terminal 1: Start the API
cd /path/to/pay_orchestrator/app
python api_server_multiregion.py

# In a new terminal: Start the Streamlit UI
streamlit run streamlit_ui_multiregion.py
```

### Option 2: Docker Compose (Production)

Update your `docker-compose.yml` to use the new multiregion services:

```yaml
api:
  build: { context: ., dockerfile: Dockerfile }
  command: uvicorn api_server_multiregion:app --host 0.0.0.0 --port 8000 --reload

ui:
  build: { context: ., dockerfile: Dockerfile }
  command: streamlit run streamlit_ui_multiregion.py --server.port 8501
```

Then run:
```bash
docker-compose up -d
```

### Option 3: Manual Setup

```bash
# Install dependencies
pip install -r requirements_web.txt --break-system-packages

# Start API (Terminal 1)
python app/api_server_multiregion.py

# Start UI (Terminal 2)
streamlit run app/streamlit_ui_multiregion.py
```

## 📋 API Endpoints

### Configuration Endpoints

**Get all available regions:**
```bash
curl http://localhost:8000/regions
```

Response:
```json
{
  "status": "success",
  "regions": {
    "ZA": "South Africa",
    "US": "United States",
    "GB": "United Kingdom",
    "EU": "Europe"
  }
}
```

**Get payment types for a region:**
```bash
curl http://localhost:8000/regions/US/payment-types
```

**Get available rails for a region:**
```bash
curl http://localhost:8000/regions/GB/rails
```

### Payment Processing

**Process a payment (multi-region):**
```bash
curl -X POST http://localhost:8000/process-payment \
  -H "Content-Type: application/json" \
  -d '{
    "region": "US",
    "payment_type": "Domestic Wire Transfer",
    "amount": 50000,
    "sender_country": "US",
    "receiver_country": "US",
    "from_currency": "USD",
    "to_currency": "USD",
    "sender_account": "1234567890",
    "receiver_account": "0987654321",
    "optimization": "Speed-Focused",
    "risk_tolerance": "Medium",
    "compliance": {
      "aml_check": true,
      "sanctions_check": true,
      "fraud_check": true
    }
  }'
```

Response:
```json
{
  "status": "SUCCESS",
  "payment_id": "abc123def456",
  "region": "US",
  "payment_type": "Domestic Wire Transfer",
  "amount": 50000,
  "selected_rail": "FedWire",
  "processing_time_ms": 2341,
  "compliance_status": "APPROVED",
  "route_score": 92.5,
  "estimated_cost": 15.00,
  "rails_considered": [
    {
      "rail": "FedWire",
      "score": 92.5,
      "type": "DOMESTIC_EXPRESS",
      "speed": "30 minutes",
      "cost": "$15.00",
      "availability": "99.99%"
    },
    ...
  ],
  "execution_details": {
    "optimization": "Speed-Focused",
    "risk_tolerance": "Medium",
    "compliance_checks": {...},
    "currency_pair": "USD/USD",
    "processing_time_ms": 2341,
    "timestamp": "2024-05-12T10:30:45.123456"
  }
}
```

## 🎮 Web Interface Features

### Tab 1: Process Payment
- Region selector dropdown
- Region-specific payment type selection
- Currency pair selection
- Amount input
- Compliance options (AML, Sanctions, Fraud)
- Optimization preference (Speed/Cost/Balanced)
- Risk tolerance slider

### Tab 2: Available Rails
- Region-specific rail cards
- Processing time
- Cost per transaction
- Success rate
- Availability percentage

### Tab 3: Metrics
- Daily transaction count
- Success rate
- Average processing time
- Cost savings
- Rail usage distribution by region

### Tab 4: Logs
- Real-time processing logs
- Timestamp tracking
- Log levels (INFO, WARNING, ERROR)
- Clear logs option

## 🔧 Configuration Files

### `/config/regions_config.py`
- Complete regional configurations
- Payment types per region
- Rail definitions per region
- Corridor mappings
- Currency information

### `/api_server_multiregion.py`
- FastAPI endpoints for multi-region support
- Regional rail selection logic
- Payment processing pipeline
- Compliance validation
- Cost calculation

### `/streamlit_ui_multiregion.py`
- Multi-region UI with dropdown
- Dynamic payment type loading
- Region-specific rail display
- Metrics dashboard per region

## 🎯 Usage Examples

### Example 1: US Domestic Wire Transfer

1. Open Streamlit UI at `http://localhost:8501`
2. Select region: **🇺🇸 United States**
3. Select payment type: **Domestic Wire Transfer**
4. Enter amount: **$50,000**
5. Select optimization: **Speed-Focused**
6. Click **Process Payment**

Expected: FedWire selected (fastest option)

### Example 2: European SEPA Instant Transfer

1. Select region: **🇪🇺 Europe**
2. Select payment type: **SEPA Instant**
3. Enter amount: **€100,000**
4. Select optimization: **Speed-Focused**
5. Click **Process Payment**

Expected: SEPA_INST selected (10-second processing)

### Example 3: Cost-Optimized UK Bulk Transfer

1. Select region: **🇬🇧 United Kingdom**
2. Select payment type: **BACS Transfer**
3. Enter amount: **£150,000**
4. Select optimization: **Cost-Focused**
5. Click **Process Payment**

Expected: BACS selected (cheapest option at $0.15)

## 🔐 Security Features

- Region validation
- Compliance checks (AML, Sanctions, Fraud)
- Payment amount validation against rail limits
- Risk tolerance assessment
- Thread-safe logging
- CORS enabled for frontend integration

## 📊 Rail Selection Algorithm

The AI-driven rail selector uses a composite scoring system:

```
Score = (Speed × Weight) + (Cost × Weight) + 
         (Availability × 0.2) + (Compatibility × 10) + 
         (Risk Adjustment)

Where:
- Speed Weight = 0.5 for Speed-Focused, 0.3 for others
- Cost Weight = 0.5 for Cost-Focused, 0.3 for others
- Availability = Uptime percentage (0-1)
- Compatibility = 10 if amount <= rail_max, 0 otherwise
- Risk Adjustment = Bonus based on risk level
```

## 🐛 Troubleshooting

### "Invalid region" error
- Check region code is uppercase (ZA, US, GB, EU)
- Verify region exists in `/config/regions_config.py`

### "No rails configured for region" error
- Ensure region configuration has rails defined
- Check `/config/regions_config.py` for completeness

### Streamlit shows empty payment types
- Verify region selection is working
- Check browser console for errors
- Restart Streamlit server

### API returning 400 errors
- Validate JSON payload format
- Check currency codes (3 letters, uppercase)
- Verify region code exists

## 📈 Next Steps

### Phase 2: Production Features
1. Database integration for payment history
2. Real FX rate API integration
3. Temporal workflow integration
4. LangSmith monitoring
5. Advanced compliance rules engine

### Phase 3: Advanced Features
1. Multi-currency wallet support
2. Scheduled payment recurring
3. Invoice-based payments
4. Batch processing UI
5. Advanced reporting dashboard

## 📞 Support

For issues or questions:
1. Check the logs tab in the UI
2. Review API response details
3. Consult `/config/regions_config.py` for regional specs
4. Check terminal output for detailed error messages

---

**Version:** 2.0.0 Multi-Region  
**Built for:** ZA, US, GB, EU  
**Status:** Production Ready ✅
