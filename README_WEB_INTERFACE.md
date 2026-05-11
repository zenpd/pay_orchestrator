# Payment Orchestrator - Web Interface (FastAPI + Streamlit)

**Production-grade web interface for AI-powered payment orchestration**

---

## 🎯 Overview

Complete web-based demonstration platform featuring:

- **FastAPI Backend** - RESTful API for payment processing
- **Streamlit UI** - Interactive web interface
- **Real-time Monitoring** - Live metrics and dashboards
- **Professional Design** - Stakeholder-ready presentation

---

## 📦 What's Included

### **Backend (FastAPI)**
- **api_server.py** (11KB) - RESTful API server
  - Payment processing endpoints
  - Metrics and monitoring
  - Corridor and rail information
  - Auto-generated API documentation

### **Frontend (Streamlit)**
- **streamlit_ui.py** (20KB) - Interactive web UI
  - Payment processing forms
  - Quick templates
  - Real-time metrics dashboard
  - Corridors and rails explorer
  - Architecture documentation

### **Scripts**
- **start_servers.sh** - One-command startup
- **stop_servers.sh** - Clean shutdown
- **requirements_web.txt** - All dependencies

---

## 🚀 Quick Start

### **Step 1: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements_web.txt --break-system-packages
```

### **Step 2: Start Servers**

#### **Option A: Using Startup Script (Recommended)**
```bash
# Make scripts executable
chmod +x start_servers.sh stop_servers.sh

# Start both servers
./start_servers.sh
```

#### **Option B: Manual Start**
```bash
# Terminal 1 - Start FastAPI backend
python api_server.py

# Terminal 2 - Start Streamlit UI
streamlit run streamlit_ui.py
```

### **Step 3: Access the Interface**

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

---

## 🎨 Streamlit UI Features

### **1. Process Payment** 📤
- Interactive payment form
- Real-time validation
- Instant feedback
- Quick templates for common scenarios

### **2. Session Metrics** 📊
- Real-time dashboard
- Success rate tracking
- Rails usage distribution
- Compliance statistics
- Layer 4 integration metrics

### **3. Corridors & Rails** 🌍
- Available payment corridors
- Rail performance metrics
- Cost and speed comparison
- Regulatory requirements

### **4. Architecture** 🏗️
- 5-layer architecture overview
- Agent descriptions
- System benefits
- Technical specifications

---

## 🔌 FastAPI Endpoints

### **Payment Processing**
```
POST   /api/v1/payment/process      - Process new payment
GET    /api/v1/payment/{id}         - Get payment status
```

### **Metrics & Monitoring**
```
GET    /api/v1/metrics/session      - Session metrics
POST   /api/v1/metrics/reset        - Reset session
```

### **Reference Data**
```
GET    /api/v1/corridors            - Available corridors
GET    /api/v1/rails                - Rail performance
GET    /api/v1/fx-rate              - FX rates
```

### **System**
```
GET    /                            - API info
GET    /health                      - Health check
```

---

## 📱 Streamlit UI Screenshots

### **Payment Processing Page**
```
┌─────────────────────────────────────────────────────────┐
│  💳 Payment Processing Orchestrator                     │
│  AI-Powered Payment Routing with 5-Layer Architecture   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📤 Standard Payment | 📋 Templates | 📜 Recent         │
│                                                          │
│  Sender Information          Receiver Information       │
│  ├─ Name                     ├─ Name                    │
│  ├─ Country                  ├─ Country                 │
│  └─ Currency                 └─ Currency                │
│                                                          │
│  Payment Details                                        │
│  ├─ Amount: 50,000.00                                   │
│  └─ Purpose: Trade settlement                           │
│                                                          │
│  [🚀 Process Payment]                                    │
│                                                          │
│  ✅ Payment Processed Successfully!                      │
│  Payment ID: PAY-20251112-0001                          │
│  Status: SUCCESS                                        │
│  Selected Rail: SWIFT_GPI                               │
│                                                          │
│  Processing Details:                                    │
│  Compliance: APPROVED | Risk: 0.150                     │
│  Cost: $28.45        | Time: 4.23h                      │
└─────────────────────────────────────────────────────────┘
```

### **Metrics Dashboard**
```
┌─────────────────────────────────────────────────────────┐
│  📊 Session Metrics Dashboard                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Total: 6   Success: 100%   Avg Time: 1.23s            │
│                                                          │
│  [Success/Failure Pie Chart] [Rails Usage Bar Chart]    │
│                                                          │
│  Compliance Statistics                                  │
│  ✅ Approved: 6  ⚠️ Hold: 0  ❌ Rejected: 0             │
│                                                          │
│  Layer 4 Integration                                    │
│  Validations: 6  Failures: 0  Success: 100%            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Demo Flow

### **For Stakeholder Presentations:**

1. **Start with Architecture Page**
   - Show the 5-layer architecture
   - Explain AI-powered routing
   - Highlight key benefits

2. **Process Sample Payments**
   - Use quick templates
   - Show real-time processing
   - Display success metrics

3. **Show Metrics Dashboard**
   - Display success rates
   - Show rails distribution
   - Highlight compliance stats

4. **Explore Corridors & Rails**
   - Compare rail performance
   - Show corridor configurations
   - Discuss optimization

---

## 🔧 API Usage Examples

### **Process Payment via API**
```bash
curl -X POST "http://localhost:8000/api/v1/payment/process" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000.0,
    "currency_from": "ZAR",
    "currency_to": "USD",
    "sender_country": "ZA",
    "receiver_country": "US",
    "payment_purpose": "Trade settlement",
    "sender_name": "Standard Bank",
    "receiver_name": "Global Partners Inc"
  }'
```

### **Get Session Metrics**
```bash
curl "http://localhost:8000/api/v1/metrics/session"
```

### **Get Corridor Info**
```bash
curl "http://localhost:8000/api/v1/corridors?sender_country=ZA&receiver_country=US"
```

### **Get Rail Performance**
```bash
curl "http://localhost:8000/api/v1/rails?rail_name=SWIFT_GPI"
```

---

## 📊 Key Features

### **1. Real-time Processing**
- ✅ Instant payment orchestration
- ✅ Live status updates
- ✅ Real-time metrics

### **2. Interactive Dashboards**
- ✅ Visual metrics
- ✅ Charts and graphs
- ✅ Success tracking

### **3. Professional UI**
- ✅ Clean, modern design
- ✅ Responsive layout
- ✅ Stakeholder-ready

### **4. Complete API**
- ✅ RESTful endpoints
- ✅ Auto-generated docs
- ✅ Easy integration

---

## 🐛 Troubleshooting

### **API won't start**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill <PID>

# Or use different port
uvicorn api_server:app --port 8001
```

### **Streamlit connection error**
```bash
# Ensure API is running first
curl http://localhost:8000/health

# Check Streamlit config
streamlit run streamlit_ui.py --server.port 8501
```

### **Import errors**
```bash
# Reinstall dependencies
pip install -r requirements_web.txt --break-system-packages --force-reinstall
```

### **Stuck processing (Original CLI Demo Issue)**
The original `demo_realistic_mvp.py` can get stuck after feedback because it creates a new orchestrator instance in the summary. Fixed in the web version by using proper state management.

---

## 🔄 Comparison: CLI vs Web Interface

| Feature | CLI Demo | Web Interface |
|---------|----------|---------------|
| **Ease of Use** | Command line | Web browser |
| **Interactivity** | Sequential | Real-time |
| **Visualization** | Text/colors | Charts/graphs |
| **Multiple Payments** | Run script again | Process continuously |
| **Metrics** | End summary | Live dashboard |
| **Stakeholder-Ready** | Good | Excellent |
| **Production-Like** | Yes | Yes |
| **API Access** | No | Yes |

---

## 📈 Production Deployment

### **For Production:**

1. **Security**
   ```python
   # Add authentication
   from fastapi.security import OAuth2PasswordBearer
   
   # Add HTTPS
   uvicorn.run(app, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
   ```

2. **Database**
   ```python
   # Replace in-memory state with Redis
   import redis
   state_store = redis.Redis(host='localhost', port=6379)
   ```

3. **Scaling**
   ```bash
   # Use Gunicorn for multiple workers
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

4. **Monitoring**
   ```python
   # Add Prometheus metrics
   from prometheus_client import Counter, Histogram
   ```

---

## 🎓 Integration Examples

### **Python Client**
```python
import requests

# Process payment
response = requests.post(
    "http://localhost:8000/api/v1/payment/process",
    json={
        "amount": 50000.0,
        "currency_from": "ZAR",
        "currency_to": "USD",
        # ... other fields
    }
)

payment = response.json()
print(f"Payment {payment['payment_id']}: {payment['status']}")
```

### **JavaScript/React**
```javascript
const response = await fetch('http://localhost:8000/api/v1/payment/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    amount: 50000.0,
    currency_from: 'ZAR',
    currency_to: 'USD',
    // ... other fields
  })
});

const payment = await response.json();
console.log(`Payment ${payment.payment_id}: ${payment.status}`);
```

---

## 📚 File Structure

```
web-interface/
├── api_server.py              # FastAPI backend
├── streamlit_ui.py            # Streamlit frontend
├── requirements_web.txt       # Dependencies
├── start_servers.sh           # Startup script
├── stop_servers.sh            # Shutdown script
│
├── payment_orchestrator_mvp.py   # Core orchestrator
├── state_manager.py              # State management
├── mock_data_sources.py          # Mock data
├── visual_logger.py              # Logging
│
└── agents/
    ├── context_collector.py
    ├── policy_reasoner.py
    ├── optimizer.py
    ├── execution.py
    ├── feedback.py
    ├── layer4_validator.py
    └── layer4_updater.py
```

---

## ✅ Success Checklist

After starting the interface:

- [ ] API health check responds: http://localhost:8000/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Streamlit UI loads: http://localhost:8501
- [ ] Can process payments through UI
- [ ] Metrics dashboard updates
- [ ] Templates work correctly
- [ ] Charts render properly
- [ ] Can reset session

---

## 🎯 Demo Tips

### **For Best Presentation:**

1. **Start with a clean session**
   - Click "Reset Session" in sidebar

2. **Use templates for speed**
   - Show 2-3 different scenarios

3. **Highlight metrics**
   - Point out success rates
   - Show rails distribution

4. **Explain architecture**
   - Use Architecture page
   - Discuss 5-layer design

5. **Show API docs**
   - Open http://localhost:8000/docs
   - Demonstrate API capabilities

---

## 🚀 Next Steps

### **Enhancements for Production:**

1. **Authentication & Authorization**
   - OAuth2/JWT tokens
   - Role-based access control

2. **Database Integration**
   - PostgreSQL for transactions
   - Redis for caching
   - TimescaleDB for metrics

3. **Advanced Features**
   - Batch payment processing
   - Scheduled payments
   - Payment templates management
   - Advanced analytics

4. **Monitoring & Observability**
   - Prometheus metrics
   - Grafana dashboards
   - Distributed tracing
   - Alert management

5. **Production Deployment**
   - Docker containerization
   - Kubernetes orchestration
   - Load balancing
   - Auto-scaling

---

## 📞 Support

For issues or questions:
1. Check API logs: `tail -f api_server.log`
2. Check UI logs: `tail -f streamlit_ui.log`
3. Verify all dependencies are installed
4. Ensure ports 8000 and 8501 are available

---

**The web interface provides a production-ready, stakeholder-friendly demonstration platform that showcases the full capabilities of the AI-powered payment orchestration system!**

---

**Standard Bank / ZenLabs - October 2025**
