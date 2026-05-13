#!/bin/bash
# Simple deployment script for Payment Orchestrator

set -e

ACR_NAME="zafacr"
ACR_URL="zafacr-gqfyc3h8eya2djey.azurecr.io"
RESOURCE_GROUP="Zenlabs-Agent-Foundry"
ACA_ENV="zaf-aca-pvt-env"
REGION="eastus2"
BACKEND_APP="payment-orchestrator-be"
FRONTEND_APP="payment-orchestrator-fe"

echo "🔏 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "✨ Creating backend container app..."
az containerapp create \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENV \
  --image "$ACR_URL/$BACKEND_APP:latest" \
  --target-port 8005 \
  --ingress internal \
  --cpu 1.0 \
  --memory 2Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars APP_ENV=production LOG_LEVEL=INFO \
  --registry-server "$ACR_URL" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD"

echo "✨ Creating frontend container app..."
az containerapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENV \
  --image "$ACR_URL/$FRONTEND_APP:latest" \
  --target-port 5173 \
  --ingress external \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 1 \
  --max-replicas 2 \
  --env-vars VITE_API_URL="https://$BACKEND_APP.bravesky-d9f9eeb7.$REGION.azurecontainerapps.io/api" \
  --registry-server "$ACR_URL" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 URLs:"
echo "  Backend:  https://$BACKEND_APP.bravesky-d9f9eeb7.$REGION.azurecontainerapps.io"
echo "  Frontend: https://$FRONTEND_APP.bravesky-d9f9eeb7.$REGION.azurecontainerapps.io"
