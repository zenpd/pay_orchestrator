# Azure Container Apps Deployment Guide

## Prerequisites

- Azure CLI installed and authenticated
- Resource Group: `Zenlabs-Agent-Foundry`
- Azure Container Environment: `zaf-aca-pvt-env`
- VNet: `zaf-us2-vnet` (10.1.4.0/23)
- PostgreSQL and Redis available
- Azure Container Registry: `zafacr`

## Deployment Steps

### 1. Create Backend Container App

```bash
az containerapp create \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --environment zaf-aca-pvt-env \
  --image zafacr.azurecr.io/payment-orchestrator-be:latest \
  --target-port 8005 \
  --ingress internal \
  --cpu 1.0 \
  --memory 2Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    DATABASE_URL="postgresql+asyncpg://postgres:password@postgresql-internal:5432/payment_orchestrator" \
    REDIS_URL="redis://redis-internal:6379/0" \
    CORS_ALLOWED_ORIGINS="https://payment-orchestrator-fe.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io" \
  --secrets \
    "db-url=postgresql+asyncpg://postgres:password@postgresql-internal:5432/payment_orchestrator" \
    "openai-key=your-api-key" \
  --registry-server zafacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

### 2. Create Frontend Container App

```bash
az containerapp create \
  --name payment-orchestrator-fe \
  --resource-group Zenlabs-Agent-Foundry \
  --environment zaf-aca-pvt-env \
  --image zafacr.azurecr.io/payment-orchestrator-fe:latest \
  --target-port 5173 \
  --ingress external \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 1 \
  --max-replicas 2 \
  --env-vars \
    VITE_API_URL="https://payment-orchestrator-be.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io/api" \
  --registry-server zafacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

### 3. Update Environment Variables in Key Vault

```bash
# For production credentials
az keyvault secret set \
  --vault-name zaf-kv-01 \
  --name payment-db-url \
  --value "postgresql+asyncpg://postgres:password@postgresql-interval:5432/payment_orchestrator"

az keyvault secret set \
  --vault-name zaf-kv-01 \
  --name payment-redis-url \
  --value "redis://redis-internal:6379/0"

az keyvault secret set \
  --vault-name zaf-kv-01 \
  --name payment-openai-key \
  --value "your-api-key"
```

### 4. Enable Azure Pipelines CI/CD

Configure Azure Pipelines to automatically:
1. Build Docker images on `main` branch push
2. Push to Azure Container Registry
3. Deploy new revisions to Container Apps

Pipeline files already created:
- `azure-pipelines-be.yml` — Backend pipeline
- `azure-pipelines-fe.yml` — Frontend pipeline

### 5. Verify Deployment

```bash
# Check container app status
az containerapp show \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry

# Get current revision
az containerapp revision list \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry

# View logs
az containerapp logs show \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --follow

# Health check
curl https://payment-orchestrator-be.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io/health
```

## Networking

- **Backend**: Internal ingress (only accessible within VNet)
- **Frontend**: External ingress (public access)
- **Database**: PostgreSQL on VNet at `postgresql-internal:5432`
- **Cache**: Redis on VNet at `redis-internal:6379`

## Auto-Scaling Configuration

- **Backend**: 1-3 replicas based on CPU/memory
- **Frontend**: 1-2 replicas based on request volume

## Monitoring

- **Application Insights**: Connected for tracing and metrics
- **Phoenix**: Distributed tracing endpoint (if configured)
- **Logs**: JSON structured logs to stdout
- **Alerts**: Set thresholds for error rates and latency

## Troubleshooting

### Container fails to start
```bash
# Check logs
az containerapp logs show --name payment-orchestrator-be --resource-group Zenlabs-Agent-Foundry --follow

# Verify environment variables
az containerapp show --name payment-orchestrator-be --resource-group Zenlabs-Agent-Foundry --query "properties.template.containers[0].env"
```

### Database connection errors
```bash
# Verify PostgreSQL is accessible from ACA VNet
az containerapp exec \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --command "psql postgresql://postgres:password@postgresql-internal:5432/payment_orchestrator"
```

### Frontend can't reach API
- Ensure backend is using internal ingress
- Update frontend `VITE_API_URL` to backend's public domain
- Check CORS configuration in backend environment

## Rollback

```bash
# Revert to previous revision
az containerapp revision set-active \
  --name payment-orchestrator-be \
  --resource-group Zenlabs-Agent-Foundry \
  --revision <previous-revision-name>
```

## Cost Optimization

- Use `.5` CPU for frontend (sufficient for static content)
- Use `1.0` CPU for backend (LangGraph processing)
- Set `min-replicas=1` to minimize idle costs
- Enable auto-scaling to handle traffic spikes

## Disaster Recovery

1. **Database**: Use Azure Database for PostgreSQL backup
2. **Secrets**: Store in Azure Key Vault with backup
3. **Code**: Maintain git repository with version tags
4. **Container Images**: Retain multiple image versions in ACR
