"""Crée le workflow n8n 'Agent RAG PDF - Azure' via l'API REST."""

import json
import os
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

N8N_API_KEY     = os.getenv("N8N_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
N8N_BASE        = "http://localhost:5678/api/v1"
WORKFLOW_FILE   = Path("workflow_n8n.json")

HEADERS = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": N8N_API_KEY,
}

SYSTEM_PROMPT = (
    "Tu es un assistant expert en analyse de documents IT "
    "(appels d'offres, contrats, CCTP).\n"
    "Utilise toujours l'outil RechercheDocuments pour repondre.\n"
    "Cite systematiquement : fichier source, article, numero de page."
)

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def get_or_create_mistral_cred() -> tuple[str | None, str]:
    """Retourne (id, name) du credential Mistral existant ou le crée."""
    resp = requests.get(f"{N8N_BASE}/credentials", headers=HEADERS, timeout=10)
    if resp.ok:
        for cred in resp.json().get("data", []):
            if "mistral" in cred.get("type", "").lower():
                print(f"  [INFO] Credential Mistral existant : {cred['id']} ({cred['name']})")
                return cred["id"], cred["name"]

    print("  [INFO] Aucun credential Mistral trouvé — création en cours...")
    body = {
        "name": "Mistral Cloud API",
        "type": "mistralCloudApi",
        "data": {"apiKey": MISTRAL_API_KEY},
    }
    resp = requests.post(f"{N8N_BASE}/credentials", headers=HEADERS, json=body, timeout=10)
    if resp.ok:
        cred = resp.json()
        print(f"  [OK] Credential Mistral créé : {cred['id']}")
        return cred["id"], cred["name"]

    print(f"  [WARN] Impossible de créer le credential : {resp.status_code} {resp.text[:120]}")
    return None, "Mistral Cloud API"


# ---------------------------------------------------------------------------
# Workflow builder
# ---------------------------------------------------------------------------

def build_workflow(mistral_cred_id: str | None, mistral_cred_name: str) -> dict:
    trigger_id  = str(uuid.uuid4())
    agent_id    = str(uuid.uuid4())
    model_id    = str(uuid.uuid4())
    memory_id   = str(uuid.uuid4())
    tool_id     = str(uuid.uuid4())
    webhook_id  = str(uuid.uuid4())

    model_node = {
        "parameters": {
            "model": "mistral-small-latest",
            "options": {},
        },
        "id": model_id,
        "name": "Mistral Chat Model",
        "type": "@n8n/n8n-nodes-langchain.lmChatMistralCloud",
        "typeVersion": 1,
        "position": [120, 280],
    }
    if mistral_cred_id:
        model_node["credentials"] = {
            "mistralCloudApi": {"id": mistral_cred_id, "name": mistral_cred_name}
        }

    nodes = [
        # 1 — Chat Trigger
        {
            "parameters": {"options": {}},
            "id": trigger_id,
            "name": "When chat message received",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "typeVersion": 1.1,
            "position": [0, 0],
            "webhookId": webhook_id,
        },
        # 2 — AI Agent
        {
            "parameters": {
                "promptType": "define",
                "text": "={{ $json.chatInput }}",
                "options": {"systemMessage": SYSTEM_PROMPT},
            },
            "id": agent_id,
            "name": "AI Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1.7,
            "position": [300, 0],
        },
        # 3 — Mistral Chat Model
        model_node,
        # 4 — Simple Memory (3 messages)
        {
            "parameters": {"contextWindowLength": 3},
            "id": memory_id,
            "name": "Simple Memory",
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "typeVersion": 1.2,
            "position": [360, 280],
        },
        # 5 — HTTP Request Tool : RechercheDocuments
        {
            "parameters": {
                "name": "RechercheDocuments",
                "description": (
                    "Recherche semantique dans les documents PDF indexes "
                    "(appels d'offres, contrats, CCTP). "
                    "Retourne la reponse et les sources (fichier, page, article)."
                ),
                "method": "POST",
                "url": "http://localhost:8000/query",
                "sendBody": True,
                "contentType": "json",
                "specifyBody": "keypair",
                "bodyParameters": {
                    "values": [
                        {
                            "name": "question",
                            "value": (
                                "={{ $fromAI('question',"
                                " 'La question a rechercher dans les documents') }}"
                            ),
                        }
                    ]
                },
                "options": {},
            },
            "id": tool_id,
            "name": "RechercheDocuments",
            "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
            "typeVersion": 1.1,
            "position": [600, 280],
        },
    ]

    connections = {
        "When chat message received": {
            "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
        },
        "Mistral Chat Model": {
            "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
        },
        "Simple Memory": {
            "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
        },
        "RechercheDocuments": {
            "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
        },
    }

    return {
        "name": "Agent RAG PDF - Azure",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Vérifier la connectivité n8n
    try:
        resp = requests.get(f"{N8N_BASE}/workflows", headers=HEADERS, timeout=8)
    except requests.ConnectionError:
        print(f"[ERREUR] n8n inaccessible sur {N8N_BASE}")
        return

    if not resp.ok:
        print(f"[ERREUR] API n8n : {resp.status_code} {resp.text[:120]}")
        return

    existing = resp.json().get("data", [])
    print(f"[OK] n8n accessible — {len(existing)} workflow(s) existant(s)")

    # 2. Credential Mistral
    print("[INFO] Recherche du credential Mistral...")
    mistral_cred_id, mistral_cred_name = get_or_create_mistral_cred()

    # 3. Supprimer l'ancien workflow du même nom si présent
    for wf in existing:
        if wf.get("name") == "Agent RAG PDF - Azure":
            del_resp = requests.delete(
                f"{N8N_BASE}/workflows/{wf['id']}", headers=HEADERS, timeout=10
            )
            if del_resp.ok:
                print(f"  [INFO] Ancien workflow supprimé : {wf['id']}")

    # 4. Créer le workflow
    print("[INFO] Création du workflow...")
    workflow = build_workflow(mistral_cred_id, mistral_cred_name)
    resp = requests.post(f"{N8N_BASE}/workflows", headers=HEADERS, json=workflow, timeout=15)

    if not resp.ok:
        print(f"[ERREUR] Création échouée : {resp.status_code} {resp.text[:300]}")
        # Sauvegarde locale du JSON quand même
        WORKFLOW_FILE.write_text(json.dumps(workflow, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INFO] JSON sauvegarde localement -> {WORKFLOW_FILE}")
        print("[INFO] Importez-le manuellement : n8n UI > Workflows > Import")
        return

    result = resp.json()
    WORKFLOW_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    wf_id = result.get("id", "?")
    print(f"[OK] Workflow créé   : ID={wf_id}")
    print(f"[OK] Nom             : {result.get('name')}")
    print(f"[OK] Fichier         : {WORKFLOW_FILE}")
    print(f"[OK] URL n8n         : http://localhost:5678/workflow/{wf_id}")
    print()
    print("[INFO] Noeuds créés  :")
    for node in result.get("nodes", []):
        print(f"         • {node['name']}  ({node['type']})")


if __name__ == "__main__":
    main()
