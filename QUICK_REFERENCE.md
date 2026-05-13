# Payment Orchestrator — Quick Reference

## 🚀 Start Here

```bash
cd /Users/sysadm/Documents/agent_foundry/pay_orchestrator

# Choose one:
make run-local        # Local dev (2 terminals)
make run-docker       # Docker Compose (all-in-one)
./deploy-aca.sh       # Azure Container Apps
```

## 📍 URLs After Start

| Service | Local | Docker | Azure |
|---------|-------|--------|-------|
| Frontend | `localhost:5173` | `localhost:5173` | Global IP |
| Backend | `localhost:8005` | `localhost:8005` | Internal |
| Docs | `localhost:8005/docs` | `localhost:8005/docs` | `/docs` |

## ⚙️ Make Commands

```bash
make setup            # Install dependencies
make run-backend      # Backend only
make run-frontend     # Frontend only
make run-docker       # Docker Compose
make stop             # Stop containers
make lint             # Check code quality
make format           # Format code
make clean            # Clean artifacts
```

## 🧪 Test Orchestration

**Via UI**: Visit frontend, fill form, click "Orchestrate"

**Via curl**:
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

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `SETUP_AND_DEPLOY.md` | **START HERE** — Complete setup guide |
| `REFACTORING_GUIDE.md` | Architecture and standards |
| `ACA_DEPLOYMENT_GUIDE.md` | Azure deployment details |
| `REFACTORING_CHECKLIST.md` | Implementation checklist |

## 🔧 Configuration

```bash
cd app
cp .env.example .env
# Edit .env with your credentials
```

**Key Variables**:
- `APP_ENV`: development / production
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection  
- `CORS_ALLOWED_ORIGINS`: Frontend URLs
- `AZURE_OPENAI_ENDPOINT/KEY`: LLM credentials

## 🚢 Deployment Checklist

- [ ] Test locally: `make run-local`
- [ ] Run tests: `make test`
- [ ] Check logs for errors
- [ ] Update `.env` with production creds
- [ ] Deploy: `./deploy-aca.sh`
- [ ] Verify health: `curl https://.../health`
- [ ] Test API endpoints
- [ ] Monitor logs in Application Insights

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | `python --version` (need 3.12+), check `.env` |
| Frontend can't reach API | Verify `CORS_ALLOWED_ORIGINS`, backend port 8005 |
| Database connection fails | Check `DATABASE_URL` in `.env`, PostgreSQL running |
| `make` commands not found | `which make` (install if needed) |
| Docker issues | `make clean && make run-docker` |

## 📦 Project Files

```
pay_orchestrator/
├── app/                    ← Main application (backend + frontend)
│   ├── api/               FastAPI routers
│   ├── agents/            LangGraph agents
│   ├── ui/                React frontend
│   ├── config/            Settings
│   ├── .env               Configuration
│   └── docker-compose.yml  Local dev environment
├── Dockerfile.refactored   Backend Docker image
├── Makefile               Development commands
├── deploy-aca.sh         ACA deployment
├── azure-pipelines-*.yml  CI/CD pipelines
└── *.md                   Documentation
```

## 💡 Key Features

✅ Payment rail orchestration (6 rails)  
✅ LangGraph agent-based workflow  
✅ Composite scoring algorithm  
✅ React + TypeScript frontend  
✅ FastAPI backend  
✅ PostgreSQL + Redis  
✅ Phoenix observability  
✅ Azure Container Apps ready  
✅ Auto-scaling configured  
✅ CI/CD pipelines included  

## 🔗 Quick Links

- **Backend API**: http://localhost:8005/docs
- **Frontend**: http://localhost:5173
- **Git Repo**: https://dev.azure.com/Zenlabs-Agent-Foundry/Zenlabs-Agent-Foundry/_git/pay_orchestrator
- **Documentation**: `SETUP_AND_DEPLOY.md`

## 📞 Common Tasks

**Restart backend**:
```bash
# Kill current process (Ctrl+C)
make run-backend
```

**Restart frontend**:
```bash
# Kill current process (Ctrl+C)
make run-frontend
```

**Check backend logs**:
```bash
# Already displayed in terminal running `make run-backend`
# Or view Docker logs:
docker logs -f payment-orchestrator-be
```

**Update dependencies**:
```bash
pip install -r requirements_refactored.txt
```

**Rebuild frontend**:
```bash
cd app/ui
npm install
npm run build
```

## 🎯 Payment Rails

| Rail | Category | Cost | Speed | Best For |
|------|----------|------|-------|----------|
| SWIFT_GPI | Cross-border | $$$ | ⚡ | Large amounts |
| NAMPAY | Cross-border | $$ | ⚡ | Cost effective |
| PARTNER_NETWORK | Cross-border | $ | ⏱️  | Ultra cheap |
| RTGS_BULK | Domestic | $ | ⏱️  | Bulk transfers |
| BATCH_ACH | Domestic | $ | ⏱️  | Standard |
| SLOW_BATCH | Domestic | $ | 🐢 | Lowest cost |

---

**Need help?** See `SETUP_AND_DEPLOY.md` for detailed instructions.
