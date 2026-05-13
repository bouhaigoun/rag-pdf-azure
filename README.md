# Agent RAG — Recherche intelligente dans documents PDF

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-AI%20Search-0078D4?logo=microsoftazure&logoColor=white)
![Mistral](https://img.shields.io/badge/Mistral-AI-FF7000?logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Orchestration-EA4B71?logo=n8n&logoColor=white)

Pipeline RAG (Retrieval-Augmented Generation) pour la recherche sémantique dans des documents PDF. Indexe automatiquement les PDFs vers Azure AI Search via embeddings Mistral, expose une API Flask, et orchestre les workflows via n8n.

**185 chunks indexés · 21 PDFs (AOs IT) · Hébergement France Central (RGPD)**

---

## Stack technique

| Composant | Rôle |
|-----------|------|
| **Azure AI Search** | Index vectoriel HNSW — 1024 dimensions |
| **Azure Blob Storage** | Stockage des PDFs sources |
| **Mistral API** | Embeddings (`mistral-embed`) + génération (`mistral-large`) |
| **Flask API** | Endpoint `/query` — interface REST pour la recherche |
| **n8n** | Orchestration des workflows d'ingestion et de requête |
| **Docker Compose** | Déploiement production (n8n + Flask API) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION                                │
│                                                                 │
│   PDF upload                                                    │
│       │                                                         │
│       ▼                                                         │
│   Azure Blob Storage  ──────────────────────────────────────┐  │
│       │                                                      │  │
│       ▼  (n8n workflow)                                      │  │
│   Chunking (paragraphes)                                     │  │
│       │                                                      │  │
│       ▼                                                      │  │
│   Mistral Embeddings (mistral-embed, 1024 dims)              │  │
│       │                                                      │  │
│       ▼                                                      │  │
│   Azure AI Search Index  ◄───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         REQUÊTE                                 │
│                                                                 │
│   Question utilisateur                                          │
│       │                                                         │
│       ▼                                                         │
│   Flask API /query                                              │
│       │                                                         │
│       ├── Embedding requête (mistral-embed)                     │
│       │                                                         │
│       ├── Recherche vectorielle Azure AI Search (top-k chunks)  │
│       │                                                         │
│       ├── Prompt enrichi (contexte + question)                  │
│       │                                                         │
│       └── Mistral LLM (mistral-large) → Réponse + citations     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation et démarrage

### Prérequis

- Docker et Docker Compose installés
- Compte Azure (AI Search + Blob Storage actifs)
- Clé API Mistral

### 1. Variables d'environnement

```bash
cp .env.example .env
```

Renseigner les variables dans `.env` :

```env
# Azure
AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
AZURE_SEARCH_KEY=<admin-key>
AZURE_SEARCH_INDEX=rag-pdf-index
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_CONTAINER_NAME=pdfs

# Mistral
MISTRAL_API_KEY=<api-key>

# n8n
N8N_WEBHOOK_URL=http://n8n:5678/webhook/rag-query
```

### 2. Démarrage Docker Compose

```bash
docker compose up -d
```

Démarre :
- **Flask API** sur `http://localhost:5000`
- **n8n** sur `http://localhost:5678`

### 3. Création de l'index Azure AI Search

```bash
python scripts/setup_index.py
```

### 4. Ingestion des PDFs

Déposer les PDFs dans `docs/`, puis :

```bash
python scripts/ingest.py --source docs/
```

### 5. Import du workflow n8n

Dans l'interface n8n (`http://localhost:5678`), importer le fichier `workflow_n8n.json`.

---

## Utilisation

### API REST

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelles sont les exigences techniques pour les AOs infrastructure ?"}'
```

Réponse :

```json
{
  "answer": "Les exigences techniques incluent...",
  "sources": [
    { "filename": "ao_007.pdf", "chunk": "...", "score": 0.94 }
  ]
}
```

### Script CLI

```bash
python scripts/query.py "Quelles sont les exigences en matière de cybersécurité ?"
```

---

## Structure du projet

```
rag-pdf-azure/
├── docker-compose.yml        # Stack n8n + Flask API
├── Dockerfile                # Image Flask API
├── requirements.txt          # Dépendances Python
├── workflow_n8n.json         # Export workflow n8n (importable)
├── .env.example              # Template variables d'environnement
├── docs/                     # PDFs à ingérer (non commité)
└── scripts/
    ├── api.py                # Flask API — endpoint /query
    ├── setup_index.py        # Création index Azure AI Search
    ├── setup_azure.py        # Configuration ressources Azure
    ├── ingest.py             # Ingestion PDF → chunks → embeddings
    ├── query.py              # CLI de requête RAG
    └── create_n8n_workflow.py # Génération programmatique du workflow
```

---

## Données et conformité

| Paramètre | Valeur |
|-----------|--------|
| Région Azure | France Central |
| Documents indexés | 21 PDFs (Appels d'Offres IT) |
| Chunks | 185 |
| Modèle embeddings | `mistral-embed` (1024 dims) |
| Modèle LLM | `mistral-large` |
| Conformité | RGPD — données hébergées en France |
