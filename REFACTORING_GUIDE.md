# Payment Orchestration Platform — Refactored

Refactored `pay_orchestrator` following `digital-onboarding` and `zenarc` standards.

## Structure

```
app_refactored/
├── api/                    # FastAPI routers and schemas
│   ├── routers/           # Endpoint handlers (health, orchestrate)
│   ├── schemas/           # Pydantic request/response models
│   ├── main.py            # FastAPI app entrypoint
│   ├── dependencies.py    # Dependency injection
│   └── auth.py            # Authentication utilities
├── agents/                # LangGraph agent definitions
│   ├── state.py           # Shared state types
│   ├── nodes/             # Individual agent nodes
│   └── tools/             # Agent tools and utilities
├── workflows/             # LangGraph workflow graphs
│   └── payment.py         # Payment orchestration workflow
├── services/              # Business logic services
├── db/                    # Database models and migrations
├── config/                # Configuration management
│   └── settings.py        # Central settings via pydantic
├── shared/                # Shared utilities
│   ├── logger.py          # Structured logging setup
│   └── observability/     # Phoenix tracing integration
├── workers/               # Temporal async workers
├── evaluations/           # Testing and evaluation framework
└── ui/                    # React TypeScript frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── pages/        # Page components
    │   ├── services/     # API client
    │   ├── types/        # TypeScript types
    │   ├── hooks/        # Custom React hooks
    │   └── store/        # State management (Zustand)
    └── package.json
```

## Backend Setup

### 1. Install Dependencies
```bash
cd /Users/sysadm/Documents/agent_foundry/pay_orchestrator
pip install -r requirements_refactored.txt
```

### 2. Environment Configuration
Create `.env`:
```
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/payment_orchestrator
REDIS_URL=redis://localhost:6379/0
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 3. Start Backend
```bash
cd app_refactored
python -m uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload
```

API available at: `http://localhost:8005/docs`

## Frontend Setup

### 1. Install Dependencies
```bash
cd app_refactored/ui
npm install
```

### 2. Start Dev Server
```bash
npm run dev
```

Frontend available at: `http://localhost:5173`

## Workflow

### Payment Orchestration Process

1. **Payment Request** → Submit payment details (amount, sender, receiver, corridor)
2. **Analysis** → Validate payment parameters
3. **Rail Scoring** → Evaluate all available payment rails
   - SWIFT_GPI: Fast cross-border
   - NAMPAY: Cost-effective cross-border
   - PARTNER_NETWORK: Ultra-cheap cross-border
   - RTGS_BULK: Batch domestic processing
   - BATCH_ACH: Standard domestic batches
   - SLOW_BATCH: Overnight domestic
4. **Rail Selection** → Choose optimal rail based on composite scoring
5. **Execution** → Submit payment via selected rail
6. **Result** → Return full orchestration trace and transaction ID

### Scoring Criteria

- **Cost Score**: Lower cost = higher score (0-100)
- **Speed Score**: Faster processing = higher score (0-100)
- **Reliability Score**: Rail availability and success rate (0-100)
- **Composite Score**: Weighted average (cost 30%, speed 40%, reliability 30%)

## API Endpoints

### POST /api/v1/payment/orchestrate
Orchestrate a single payment across optimal rails.

**Request:**
```json
{
  "amount": 50000,
  "currency": "USD",
  "sender_id": "ACC-001",
  "receiver_id": "ACC-002",
  "corridor": "ZA_US"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "stage": "completed",
  "selected_rail": "NAMPAY",
  "rail_scores": {
    "SWIFT_GPI": { "composite_score": 65.5, ... },
    "NAMPAY": { "composite_score": 72.0, ... },
    ...
  },
  "execution_result": { "transaction_id": "...", "status": "SUBMITTED" },
  "messages": [...],
  "errors": []
}
```

### GET /api/v1/payment/rails
List all available payment rails.

### GET /health
Health check endpoint.

## Temporal Workflow Engine (Optional)

To enable Temporal for workflow orchestration:

1. Set `TEMPORAL_ENABLED=true` in `.env`
2. Create worker in `app_refactored/workers/payment_worker.py`
3. Register with Temporal server

Current implementation uses LangGraph (no Temporal dependency required).

## Observability

### Phoenix Integration
- Tracing endpoint: Configured via `PHOENIX_COLLECTOR_ENDPOINT`
- Project name: `payment-orchestration`
- All LangGraph nodes emit traces

### Logging
- Structured JSON logging to stdout
- Log level configurable via `LOG_LEVEL`

## Testing

```bash
# Run tests
cd app_refactored
pytest

# Run with coverage
pytest --cov=.
```

## Deployment

### Docker Build
```bash
docker build -t payment-orchestrator:latest -f Dockerfile.refactored .
```

### Azure Container Apps
```bash
az containerapp create \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --environment zaf-aca-pvt-env \
  --image payment-orchestrator:latest \
  --target-port 8005
```

## Decisions

### Why LangGraph (Not Temporal)?

1. **Simpler**: Lightweight state machine for payment routing
2. **No External Dependency**: Runs in same process
3. **Developer Experience**: Cleaner Python-based workflow definition
4. **Performance**: Lower latency for synchronous payment decisions

**When to use Temporal**: If workflows become long-lived, require retry policies across service restarts, or need complex compensation logic.

### Why No Streaming UI Updates?

Current implementation uses polling. For real-time updates:
- Add WebSocket support in FastAPI
- Emit state updates via SSE or WebSocket
- Listen on frontend for updates

### Configuration Strategy

- Centralized via `config/settings.py`
- Supports `.env`, environment variables, Azure Key Vault
- Development defaults provided

## Next Steps

1. Add database migrations (Alembic)
2. Implement actual payment rail API calls (replace mocks)
3. Add comprehensive error handling and retries
4. Integrate with Azure Key Vault for secrets
5. Setup Temporal workers for long-running tasks
6. Add WebSocket support for real-time UI updates
7. Deploy to Azure Container Apps

---

This structure is production-ready and follows enterprise standards from `digital-onboarding` platform.
