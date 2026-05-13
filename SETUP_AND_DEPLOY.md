# Payment Orchestrator — Complete Setup & Deployment Guide

## 📍 What You Have

✅ **Backend** (FastAPI + LangGraph)
- Production-ready payment orchestration workflow
- 6 intelligent payment rails with composite scoring
- Async SQLAlchemy with PostgreSQL
- Redis for session caching
- Structured JSON logging with Phoenix integration
- Health checks and OpenAPI documentation

✅ **Frontend** (React + TypeScript)
- Modern SPA with Tailwind CSS styling
- Real-time rail scoring visualization
- Payment orchestration form
- Result tracking and transaction display

✅ **Infrastructure**
- Docker images for both backend and frontend
- Docker Compose for local development
- Azure Pipelines CI/CD configuration  
- ACA deployment scripts
- Production-ready Dockerfile with health checks

✅ **Documentation**
- This guide for complete setup
- API documentation (auto-generated OpenAPI)
- Deployment guides (local, Docker, ACA)

## 🚀 Getting Started (Choose Your Path)

### Path 1: Local Development (Fastest - 5 minutes)

```bash
# 1. Setup
cd /Users/sysadm/Documents/agent_foundry/pay_orchestrator
make setup

# 2. Run Backend (Terminal 1)
make run-backend

# 3. Run Frontend (Terminal 2)
make run-frontend
```

**Then visit**:
- Frontend: `http://localhost:5173`
- API Docs: `http://localhost:8005/docs`

### Path 2: Docker Compose (Isolated - 10 minutes)

```bash
cd /Users/sysadm/Documents/agent_foundry/pay_orchestrator
make run-docker
```

Includes PostgreSQL, Redis, backend, and frontend automatically.

### Path 3: Azure Container Apps (Production - 30 minutes)

```bash
# Deploy to ACA
./deploy-aca.sh
```

Requires:
- Azure CLI authenticated
- Resource group: `Zenlabs-Agent-Foundry`
- ACA environment: `zaf-aca-pvt-env`
- Azure Container Registry: `zafacr`

## ✅ Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

### Step 1: Clone Repository

```bash
cd /Users/sysadm/Documents/agent_foundry/pay_orchestrator
git status  # Verify you're on main branch
```

### Step 2: Create Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install -r requirements_refactored.txt
```

### Step 4: Configure Environment

```bash
cd app_refactored
cp .env.example .env

# Edit .env with your settings:
# - DATABASE_URL: Your PostgreSQL connection
# - REDIS_URL: Your Redis connection
# - AZURE_OPENAI_ENDPOINT/KEY: Your OpenAI credentials (optional for local testing)
```

### Step 5: Run Backend

```bash
cd app_refactored
PYTHONPATH=. python -m uvicorn api.main:app --port 8005 --reload
```

**Expected output**:
```
Uvicorn running on http://0.0.0.0:8005
```

### Step 6: Run Frontend (New Terminal)

```bash
cd app_refactored/ui
npm install  # First time only
npm run dev
```

**Expected output**:
```
VITE v5.x ready in x ms
Local: http://localhost:5173/
```

### Step 7: Test the Application

1. Open `http://localhost:5173`
2. Fill in payment details:
   - Amount: 50000
   - Currency: USD
   - Sender ID: ACC-001
   - Receiver ID: ACC-002
   - Corridor: ZA_US
3. Click "Orchestrate Payment"
4. See rail scores and selected optimal rail

## 🐳 Docker Compose Setup

### One-Command Startup

```bash
make run-docker
```

This automatically:
1. Starts PostgreSQL on port 5432
2. Starts Redis on port 6379
3. Builds and starts backend on port 8005
4. Builds and starts frontend on port 5173

### Access Services

- **Frontend**: `http://localhost:5173`
- **Backend**: `http://localhost:8005`
- **API Docs**: `http://localhost:8005/docs`
- **PostgreSQL**: localhost:5432 (postgres/postgres)
- **Redis**: localhost:6379

### Stop Services

```bash
make stop
```

## 🌐 Azure Container Apps Deployment

### Prerequisites

```bash
# Verify Azure CLI is installed and authenticated
az account show
az acr list  # Verify access to container registry
```

### One-Command Deployment

```bash
./deploy-aca.sh
```

This script:
1. Builds Docker images
2. Pushes to Azure Container Registry
3. Creates/updates Container Apps
4. Configures networking and auto-scaling

### Verify Deployment

```bash
# Check backend app
az containerapp show \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry

# Check frontend app
az containerapp show \
  --name payment-orchestrator-fe \
  --resource-group Zenlabs-Agent-Foundry

# View logs
az containerapp logs show \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --follow
```

### Access Deployed Services

After deployment completes, you'll see:

```
📍 URLs:
  Backend:  https://payment-orchestrator-be.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io
  Frontend: https://payment-orchestrator-fe.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io
  Docs:     https://payment-orchestrator-be.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io/docs
```

## 📊 Testing Payment Orchestration

### Via Frontend

Simply fill the form at `http://localhost:5173` and click "Orchestrate Payment"

### Via curl (Backend)

```bash
curl -X POST http://localhost:8005/api/v1/payment/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "currency": "USD",
    "sender_id": "ACC-001",
    "receiver_id": "ACC-002",
    "corridor": "ZA_US"
  }'
```

**Expected response**:
```json
{
  "session_id": "uuid-here",
  "stage": "completed",
  "selected_rail": "NAMPAY",
  "rail_scores": {
    "NAMPAY": {
      "composite_score": 72.0,
      "estimated_cost_usd": 8.0,
      ...
    },
    ...
  },
  "execution_result": {
    "transaction_id": "txn-uuid",
    "status": "SUBMITTED"
  },
  "messages": [...],
  "errors": []
}
```

### Via API Documentation

Visit `http://localhost:8005/docs` and use the interactive Swagger UI:
1. Expand POST `/api/v1/payment/orchestrate`
2. Click "Try it out"
3. Fill in example values
4. Click "Execute"

## 🔧 Development Commands

```bash
make help              # Show all available commands
make setup            # Install all dependencies
make run-local        # Instructions for local dev
make run-backend      # Start backend only
make run-frontend     # Start frontend only
make run-docker       # Start with Docker
make stop             # Stop Docker containers
make lint             # Check code quality
make format           # Format code
make test             # Run tests
make clean            # Clean artifacts
```

## 📁 Project Structure

```
pay_orchestrator/
├── app/                        ← RENAMED from app_refactored
│   ├── api/                    FastAPI application
│   ├── agents/                 LangGraph agents
│   ├── workflows/              Payment workflows
│   ├── config/                 Configuration
│   ├── db/                     Database models
│   ├── shared/                 Utilities
│   ├── observability/          Tracing
│   ├── ui/                     React frontend
│   ├── .env                    Development config
│   └── docker-compose.yml      Local environment
├── Dockerfile.refactored       Backend Docker image
├── requirements_refactored.txt Dependencies
├── Makefile                    Development commands
├── deploy-aca.sh              ACA deployment script
├── azure-pipelines-be.yml     Backend CI/CD
├── azure-pipelines-fe.yml     Frontend CI/CD
├── README.md                  Quick reference
└── ACA_DEPLOYMENT_GUIDE.md    Detailed deployment guide
```

## 🔐 Environment Configuration

### Development (.env)

```bash
cd app
cp .env.example .env
# Edit .env with local credentials
```

Key variables:
- `APP_ENV=development`
- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/payment_orchestrator`
- `REDIS_URL=redis://localhost:6379/0`
- `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000`

### Production (Azure Key Vault)

Secrets are automatically injected from Key Vault during ACA deployment:
- Database credentials
- OpenAI API keys
- Session encryption keys

## 🚀 CI/CD Pipelines

### How It Works

1. **Push to main branch**
   ```bash
   git add .
   git commit -m "feat: your changes"
   git push origin main
   ```

2. **Automatic triggers in Azure Pipelines**:
   - Backend pipeline (if API files changed): Builds and pushes Docker image
   - Frontend pipeline (if UI files changed): Builds and deploys
   - Both deploy to Container Apps automatically

### View Pipeline Status

```bash
# List pipelines
az pipelines list --project "Zenlabs-Agent-Foundry"

# View build history
az pipelines build list --definition-ids 14 15  # Adjust IDs as needed
```

## ✨ Features

### Payment Orchestration

| Rail | Type | Cost | Speed | Use Case |
|------|------|------|-------|----------|
| SWIFT_GPI | Cross-border | $12.50 | Fast (1h) | Large amounts, urgent |
| NAMPAY | Cross-border | $8.00 | Fast (1h) | Cost-effective international |
| PARTNER_NETWORK | Cross-border | $6.00 | Medium (4h) | Ultra-cheap cross-border |
| RTGS_BULK | Domestic | $0.50 | Batch | Bulk domestic transfers |
| BATCH_ACH | Domestic | $0.20 | Batch | Standard domestic |
| SLOW_BATCH | Domestic | $0.10 | Overnight | Lowest-cost domestic |

### Scoring Algorithm

```
Composite Score = 
  (Cost Score × 0.30) +
  (Speed Score × 0.40) +
  (Reliability Score × 0.30)
```

### Observability

- ✅ JSON structured logs to stdout
- ✅ Phoenix distributed tracing (when configured)
- ✅ Application Insights metrics (ACA automatic)
- ✅ Health check endpoints
- ✅ Request/response logging

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check dependencies installed
pip list | grep -E "fastapi|langgraph|sqlalchemy"

# Check Python version
python --version  # Should be 3.12+

# Try verbose startup
python -m uvicorn api.main:app --port 8005 --log-level debug
```

### Database connection failed

```bash
# For Docker Compose: Ensure PostgreSQL is running
docker ps | grep postgres

# For local: Verify PostgreSQL is accessible
psql postgresql://postgres:postgres@localhost:5432/payment_orchestrator

# Check connection string in .env
cat app/.env | grep DATABASE_URL
```

### Frontend can't reach API

1. Verify backend is running: `curl http://localhost:8005/health`
2. Check CORS in `.env`: Should include `http://localhost:5173`
3. Check browser console for CORS errors
4. Try accessing API directly: Visit `http://localhost:8005/docs`

### Docker issues

```bash
# Clean up and restart
make clean
make run-docker

# View logs
docker-compose -f app/docker-compose.yml logs -f

# Stop all containers
docker-compose -f app/docker-compose.yml down -v
```

## 📝 Next Steps

### Before Production

- [ ] Test locally with `make run-local`
- [ ] Run tests: `make test`
- [ ] Review logs for errors
- [ ] Load test with sample payments
- [ ] Configure Azure Key Vault with production secrets
- [ ] Setup monitoring and alerts
- [ ] Document API endpoints for clients

### After Production Deployment

- [ ] Monitor Application Insights for errors
- [ ] Setup PagerDuty/alerts for failures
- [ ] Configure auto-scaling policies
- [ ] Test failover and recovery
- [ ] Schedule regular backups
- [ ] Plan disaster recovery

## 📚 Additional Resources

- **OpenAPI Docs**: `http://localhost:8005/docs` (local) or HTTPS URL (ACA)
- **Full Architecture**: See `REFACTORING_GUIDE.md`
- **Deployment Details**: See `ACA_DEPLOYMENT_GUIDE.md`
- **Completion Checklist**: See `REFACTORING_CHECKLIST.md`

## 💡 Quick Command Reference

```bash
# Start everything from scratch
cd pay_orchestrator
make setup
make run-docker

# Just backend
make run-backend

# Just frontend
make run-frontend

# With Docker (includes databases)
make run-docker

# Deploy to Azure
./deploy-aca.sh

# Stop all
make stop

# Clean up
make clean
```

---

**You're all set! Pick a path above and get started.** 🚀

Questions? Check the detailed guides or the inline code comments in `app/` directory.
