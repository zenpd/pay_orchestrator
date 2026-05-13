# Payment Orchestrator Platform

> AI-powered payment rail orchestration — intelligent routing across SWIFT, ACH, and local payment networks using LangGraph agents.

## 🚀 Quick Start

### Local Development (5 minutes)

**Prerequisites**: Python 3.12+, Node.js 18+, Docker (optional)

#### Backend

```bash
# Install dependencies
make setup

# Start backend server
make run-backend
```

Backend runs at: `http://localhost:8005`  
API Docs: `http://localhost:8005/docs`

#### Frontend

```bash
# In another terminal
make run-frontend
```

Frontend runs at: `http://localhost:5173`

### With Docker Compose

```bash
make run-docker
```

Starts PostgreSQL, Redis, backend, and frontend automatically.

## 📚 Documentation

- **[REFACTORING_GUIDE.md](./REFACTORING_GUIDE.md)** — Architecture and setup
- **[REFACTORING_CHECKLIST.md](./REFACTORING_CHECKLIST.md)** — What's implemented
- **[ACA_DEPLOYMENT_GUIDE.md](./ACA_DEPLOYMENT_GUIDE.md)** — Azure deployment
- **[QUICKSTART.sh](./QUICKSTART.sh)** — Automated setup script

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI + Uvicorn
- **Agents**: LangGraph
- **Database**: PostgreSQL (async SQLAlchemy)
- **Cache**: Redis
- **Observability**: Phoenix + JSON logging

### Frontend Stack
- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **HTTP**: Axios

### Payment Orchestration Workflow

```
Payment Request
    ↓
[Analyze] → Validate parameters
    ↓
[Score Rails] → Evaluate 6 payment rails
    ↓
     ├─ SWIFT_GPI (fast, $12.50/tx)
     ├─ NAMPAY (cost-effective, $8.00/tx)
     ├─ PARTNER_NETWORK (ultra-cheap, $6.00/tx)
     ├─ RTGS_BULK (domestic, $0.50/tx)
     ├─ BATCH_ACH (standard, $0.20/tx)
     └─ SLOW_BATCH (overnight, $0.10/tx)
    ↓
[Select] → Choose optimal rail (cost 30%, speed 40%, reliability 30%)
    ↓
[Execute] → Submit payment
    ↓
Result with transaction ID
```

## 🎯 Features

### Payment Rail Selection
- **6 supported rails** across cross-border and domestic corridors
- **Composite scoring** based on cost, speed, and reliability
- **Corridor-aware** routing (ZA_US, ZA_GB, US_GB, etc.)

### Observability
- ✅ Structured JSON logging
- ✅ Phoenix distributed tracing
- ✅ Health check endpoints
- ✅ API documentation (OpenAPI/Swagger)

### Production Ready
- ✅ Docker containerization
- ✅ Azure Container Apps deployment
- ✅ Environment-scoped configuration
- ✅ Key Vault integration ready
- ✅ Auto-scaling configuration
- ✅ CI/CD pipelines (Azure Pipelines)

## 🔧 Development

### Make Commands

```bash
make help              # Show all commands
make setup            # Install dependencies
make run-backend      # Start backend server
make run-frontend     # Start frontend dev server
make run-docker       # Docker Compose
make lint             # Run linters
make format           # Format code
make test             # Run tests
make clean            # Clean artifacts
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp app_refactored/.env.example app_refactored/.env
```

Edit credentials:
- Database URL
- Azure OpenAI endpoint/key
- CORS origins

### API Endpoints

**POST** `/api/v1/payment/orchestrate`
```json
{
  "amount": 50000,
  "currency": "USD",
  "sender_id": "ACC-001",
  "receiver_id": "ACC-002",
  "corridor": "ZA_US"
}
```

**GET** `/api/v1/payment/rails` — List available rails

**GET** `/health` — Health check

## 🚢 Deployment

### Local Testing

```bash
# Terminal 1: Backend
make run-backend

# Terminal 2: Frontend
make run-frontend

# Terminal 3: Test orchestration
curl -X POST http://localhost:8005/api/v1/payment/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "currency": "USD", "sender_id": "ACC-001", "receiver_id": "ACC-002", "corridor": "ZA_US"}'
```

### Azure Container Apps

```bash
# Deploy to ACA
./deploy-aca.sh
```

This will:
1. Build Docker images
2. Push to Azure Container Registry
3. Create/update Container Apps
4. Configure networking and auto-scaling

**URLs after deployment**:
- Frontend: `https://payment-orchestrator-fe.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io`
- Backend: `https://payment-orchestrator-be.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io`

### CI/CD with Azure Pipelines

Pipelines automatically:
1. Build Docker images on `main` branch push
2. Push to Azure Container Registry
3. Deploy new revisions

Pipeline files:
- `azure-pipelines-be.yml` — Backend
- `azure-pipelines-fe.yml` — Frontend

## 📦 Project Structure

```
pay_orchestrator/
├── app_refactored/          # Complete application
│   ├── api/                 # FastAPI routers
│   ├── agents/              # LangGraph agents
│   ├── workflows/           # Payment workflows
│   ├── config/              # Configuration
│   ├── db/                  # Database models
│   ├── shared/              # Utilities
│   ├── observability/       # Tracing
│   ├── ui/                  # React frontend
│   ├── .env                 # Development config
│   └── docker-compose.yml   # Local environment
├── Dockerfile.refactored    # Production image
├── requirements_refactored.txt # Dependencies
├── Makefile                 # Development commands
├── deploy-aca.sh           # ACA deployment script
└── azure-pipelines-*.yml   # CI/CD pipelines
```

## 🔐 Security

- ✅ Non-root container user
- ✅ Environment-scoped CORS
- ✅ Secrets in Azure Key Vault
- ✅ Internal networking for sensitive services
- ✅ Health checks for container orchestration
- ✅ Rate limiting ready

## 🧪 Testing

```bash
# Run tests
make test

# With coverage
pytest --cov=app_refactored

# Backend linting
make lint

# Format code
make format
```

## 🤝 Contributing

1. Create a feature branch
2. Make changes in `app_refactored/`
3. Test locally: `make run-local`
4. Commit: `git commit -m "feat: describe change"`
5. Push: `git push origin feature-branch`
6. Pull request to `main`

## 📖 API Documentation

Interactive API docs available at:
- **Swagger UI**: `http://localhost:8005/docs`
- **ReDoc**: `http://localhost:8005/redoc`

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check dependencies
pip list | grep langgraph

# Verify Python version
python --version  # Should be 3.12+

# Check port availability
lsof -i :8005
```

### Frontend can't connect to API
1. Check backend is running: `curl http://localhost:8005/health`
2. Verify CORS in `.env`: `CORS_ALLOWED_ORIGINS=http://localhost:5173`
3. Check frontend API URL in browser console

### Database connection errors
```bash
# Verify PostgreSQL
psql postgresql://postgres:password@localhost:5432/payment_orchestrator

# Reset database
make clean
make setup
```

## 📞 Support

- **Documentation**: See `REFACTORING_GUIDE.md`
- **Issues**: Check Azure Pipelines logs
- **Local testing**: Use `make run-docker` for isolated environment

## 📋 Checklist Before Production

- [ ] Test locally with `make run-local`
- [ ] Run tests: `make test`
- [ ] Update `.env` with production credentials
- [ ] Review `ACA_DEPLOYMENT_GUIDE.md`
- [ ] Execute deployment: `./deploy-aca.sh`
- [ ] Verify health endpoints
- [ ] Monitor logs in Application Insights
- [ ] Set up alerts for errors/latency

## 📄 License

Zenlabs Agent Foundry — Internal use only

---

**Ready to orchestrate payments? Start with `make setup` → `make run-local`** 🚀
