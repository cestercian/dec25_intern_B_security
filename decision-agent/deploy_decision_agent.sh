#!/bin/bash
set -e

# Configuration
SERVICE_NAME="decision-agent"
REGION="us-central1"

echo "Deploying $SERVICE_NAME to Cloud Run ($REGION)..."

# Deploy Command
# - Mounts HYBRID_ANALYSIS_API_KEY from Secret Manager
# - Sets USE_REAL_SANDBOX=true
# - Sets FINAL_AGENT_URL (Update this after deploying Final Agent)
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars USE_REAL_SANDBOX="true",FINAL_AGENT_URL="http://placeholder-update-me" \
  --set-secrets HYBRID_ANALYSIS_API_KEY=HYBRID_ANALYSIS_API_KEY:latest

echo "Deployment submitted."
