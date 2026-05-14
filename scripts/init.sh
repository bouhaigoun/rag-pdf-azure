#!/bin/bash
# =============================================================================
# init.sh — Script d'initialisation n8n au premier démarrage
# Crée les credentials et importe le workflow automatiquement
# Correction : attend que l'API soit vraiment prête (pas juste /healthz)
# =============================================================================

N8N_URL="http://n8n:5678"
MAX_RETRIES=40
RETRY_DELAY=3

echo "⏳ Attente démarrage n8n..."

# Attendre que l'API n8n soit vraiment prête (pas juste /healthz)
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

# Créer le credential Mistral via API n8n
echo "🔑 Création credential Mistral..."
RESPONSE=$(curl -s -X POST "$N8N_URL/api/v1/credentials" \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -d "{
    \"name\": \"Mistral Cloud account\",
    \"type\": \"mistralCloudApi\",
    \"data\": {
      \"apiKey\": \"${MISTRAL_API_KEY}\"
    }
  }")
echo "Réponse credential : $RESPONSE"

# Attendre 2 secondes avant d'importer le workflow
sleep 2

# Importer le workflow via API n8n
echo "📥 Import workflow RAG PDF..."
RESPONSE=$(curl -s -X POST "$N8N_URL/api/v1/workflows" \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  --data-binary @/app/workflow_import.json)
echo "Réponse workflow : $RESPONSE"

echo ""
echo "✅ Initialisation terminée"