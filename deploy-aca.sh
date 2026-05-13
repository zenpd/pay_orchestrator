#!/bin/bash
# Deploy Payment Orchestrator to Azure Container Apps

set -e

# Configuration
RESOURCE_GROUP="Zenlabs-Agent-Foundry"
ACA_ENV="zaf-aca-pvt-env"
REGION="eastus2"
ACR_NAME="zafacr"
ACR_URL="${ACR_NAME}.azurecr.io"

# Container Apps
BACKEND_APP="payment-orchestrator-be"
FRONTEND_APP="payment-orchestrator-fe"
BACKEND_IMAGE="payment-orchestrator-be:latest"
FRONTEND_IMAGE="payment-orchestrator-fe:latest"

echo "🚀 Deploying Payment Orchestrator to Azure Container Apps"
echo "=========================================================="
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "ACA Environment: $ACA_ENV"
echo "Region: $REGION"
echo ""

# Get ACR credentials
echo "📝 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Build and push backend image
echo "📦 Building and pushing backend image..."
az acr build \
  --registry $ACR_NAME \
  --image $BACKEND_IMAGE \
  --file Dockerfile.refactored \
  .

# Build and push frontend image
echo "📦 Building and pushing frontend image..."
az acr build \
  --registry $ACR_NAME \
  --image $FRONTEND_IMAGE \
  --file app_refactored/ui/Dockerfile \
  ./app_refactored/ui

# Check if backend app exists
if az containerapp show --name $BACKEND_APP --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "🔄 Updating existing backend app..."
    az containerapp update \
      --name $BACKEND_APP \
      --resource-group $RESOURCE_GROUP \
      --image $ACR_URL/$BACKEND_IMAGE
else
    echo "✨ Creating new backend container app..."
    az containerapp create \
      --name $BACKEND_APP \
      --resource-group $RESOURCE_GROUP \
      --environment $ACA_ENV \
      --image $ACR_URL/$BACKEND_IMAGE \
      --target-port 8005 \
      --ingress internal \
      --cpu 1.0 \
      --memory 2Gi \
      --min-replicas 1 \
      --max-replicas 3 \
      --env-vars \
        APP_ENV=production \
        LOG_LEVEL=INFO \
        CORS_ALLOWED_ORIGINS="https://${FRONTEND_APP}.bravesky-d9f9eeb7.${REGION}.azurecontainerapps.io" \
      --registry-server $ACR_URL \
      --registry-username $ACR_USERNAME \
      --registry-password $ACR_PASSWORD
fi

# Check if frontend app exists
if az containerapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "🔄 Updating existing frontend app..."
    az containerapp update \
      --name $FRONTEND_APP \
      --resource-group $RESOURCE_GROUP \
      --image $ACR_URL/$FRONTEND_IMAGE
else
    echo "✨ Creating new frontend container app..."
    az containerapp create \
      --name $FRONTEND_APP \
      --resource-group $RESOURCE_GROUP \
      --environment $ACA_ENV \
      --image $ACR_URL/$FRONTEND_IMAGE \
      --target-port 5173 \
      --ingress external \
      --cpu 0.5 \
      --memory 1Gi \
      --min-replicas 1 \
      --max-replicas 2 \
      --env-vars \
        VITE_API_URL="https://${BACKEND_APP}.bravesky-d9f9eeb7.${REGION}.azurecontainerapps.io/api" \
      --registry-server $ACR_URL \
      --registry-username $ACR_USERNAME \
      --registry-password $ACR_PASSWORD
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 URLs:"
echo "  Backend:  https://${BACKEND_APP}.bravesky-d9f9eeb7.${REGION}.azurecontainerapps.io"
echo "  Frontend: https://${FRONTEND_APP}.bravesky-d9f9eeb7.${REGION}.azurecontainerapps.io"
echo "  Docs:     https://${BACKEND_APP}.bravesky-d9f9eeb7.${REGION}.azurecontainerapps.io/docs"
echo ""
echo "🔍 Monitor deployment:"
echo "  az containerapp logs show --name $BACKEND_APP --resource-group $RESOURCE_GROUP --follow"
echo ""
