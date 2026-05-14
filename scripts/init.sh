#!/bin/bash
# =============================================================================
# init.sh — Script d'initialisation n8n au premier démarrage
# Idempotent : skip si workflow et credential existent déjà
# Compatible curlimages/curl (Alpine) — pas de jq ni python3
# =============================================================================

N8N_URL="http://n8n:5678"
MAX_RETRIES=40
RETRY_DELAY=3
CREDENTIAL_NAME="Mistral Cloud account"
WORKFLOW_NAME="Agent RAG PDF - Azure"
HARDCODED_CRED_ID="hYQphYx6HQWMdD6R"

echo "⏳ Attente démarrage n8n..."

# Attendre que l'API n8n soit vraiment prête
for i in $(seq 1 $MAX_RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    "$N8N_URL/api/v1/credentials")
  if [ "$STATUS" = "200" ]; then
    echo "✅ API n8n prête"
    break
  fi
  echo "⏳ Tentative $i/$MAX_RETRIES — status: $STATUS"
  sleep $RETRY_DELAY
done

# ── Credential Mistral ────────────────────────────────────────────────────────

echo "🔍 Vérification credential '$CREDENTIAL_NAME'..."
CREDS_RESPONSE=$(curl -s \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "$N8N_URL/api/v1/credentials")

# Extraire l'ID du credential si déjà existant (sed split sur },{)
CREDENTIAL_ID=$(echo "$CREDS_RESPONSE" \
  | sed 's/},{/}\n{/g' \
  | grep "\"name\":\"${CREDENTIAL_NAME}\"" \
  | grep -o '"id":"[^"]*"' \
  | head -1 \
  | cut -d'"' -f4)

if [ -n "$CREDENTIAL_ID" ]; then
  echo "⏭️  Credential déjà existant (id: $CREDENTIAL_ID) — skip"
else
  echo "🔑 Création credential Mistral..."
  CRED_RESPONSE=$(curl -s -X POST "$N8N_URL/api/v1/credentials" \
    -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    -d "{
      \"name\": \"${CREDENTIAL_NAME}\",
      \"type\": \"mistralCloudApi\",
      \"data\": {
        \"apiKey\": \"${MISTRAL_API_KEY}\"
      }
    }")
  echo "Réponse credential : $CRED_RESPONSE"

  CREDENTIAL_ID=$(echo "$CRED_RESPONSE" \
    | grep -o '"id":"[^"]*"' \
    | head -1 \
    | cut -d'"' -f4)
fi

if [ -z "$CREDENTIAL_ID" ]; then
  echo "❌ Impossible d'obtenir l'ID du credential — abandon"
  exit 1
fi
echo "✅ Credential ID : $CREDENTIAL_ID"

# ── Workflow ──────────────────────────────────────────────────────────────────

echo "🔍 Vérification workflow '$WORKFLOW_NAME'..."
WFS_RESPONSE=$(curl -s \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "$N8N_URL/api/v1/workflows")

if echo "$WFS_RESPONSE" | grep -q "\"name\":\"${WORKFLOW_NAME}\""; then
  echo "⏭️  Workflow déjà existant — skip"
else
  echo "📥 Import workflow RAG PDF..."
  # Remplacer l'ID credential hardcodé par le nouvel ID avant import
  WORKFLOW_JSON=$(sed "s/${HARDCODED_CRED_ID}/${CREDENTIAL_ID}/g" /app/workflow_import.json)

  WF_RESPONSE=$(echo "$WORKFLOW_JSON" | curl -s -X POST "$N8N_URL/api/v1/workflows" \
    -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    --data-binary @-)
  echo "Réponse workflow : $WF_RESPONSE"
fi

echo ""
echo "✅ Initialisation terminée"