#!/bin/bash
set -e

ACR_URL="zafacr-gqfyc3h8eya2djey.azurecr.io"
ACR_USER="zafacr"
ACR_PASS="FKZSP1v13KwyQk4qPIJSJaIZ1Sx1xkASfp1ZnBwN5YmzAdmtHzskJQQJ99CBACHYHv6Eqg7NAAACAZCRoXHy"
RG="Zenlabs-Agent-Foundry"
BE_FQDN="payment-orchestrator-be.internal.bravesky-d9f9eeb7.eastus2.azurecontainerapps.io"

echo "Updating backend..."
az containerapp update \
  --name payment-orchestrator-be \
  --resource-group "$RG" \
  --image "$ACR_URL/payment-orchestrator-be:v1" \
  --set-env-vars APP_ENV=production LOG_LEVEL=INFO \
  --registry-server "$ACR_URL" \
  --registry-username "$ACR_USER" \
  --registry-password "$ACR_PASS"

echo ""
echo "Updating frontend..."
az containerapp update \
  --name payment-orchestrator-fe \
  --resource-group "$RG" \
  --image "$ACR_URL/payment-orchestrator-fe:v1" \
  --set-env-vars "VITE_API_URL=https://$BE_FQDN/api" \
  --registry-server "$ACR_URL" \
  --registry-username "$ACR_USER" \
  --registry-password "$ACR_PASS"

echo ""
echo "Done! Checking status..."
az containerapp show --name payment-orchestrator-be --resource-group "$RG" --query "{state:properties.provisioningState,image:properties.template.containers[0].image}" -o table
az containerapp show --name payment-orchestrator-fe --resource-group "$RG" --query "{state:properties.provisioningState,image:properties.template.containers[0].image}" -o table
