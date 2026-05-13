# RAG PDF Azure

Pipeline RAG (Retrieval-Augmented Generation) pour l'indexation et la recherche sémantique de documents PDF, orchestré via n8n, hébergé sur Azure.

## Stack

| Composant | Rôle |
|---|---|
| **Azure Blob Storage** | Stockage des PDFs bruts |
| **Azure AI Search** | Index vectoriel + recherche sémantique |
| **Mistral API** | Embeddings (`mistral-embed`) + génération (`mistral-large`) |
| **n8n** | Orchestration des workflows d'ingestion et de query |

## Architecture

```
PDF upload
    │
    ▼
Azure Blob Storage
    │
    ▼ (n8n workflow)
Chunking + Mistral Embeddings
    │
    ▼
Azure AI Search Index
    │
    ▼ (query workflow)
Retrieval → Mistral LLM → Réponse
```

## Démarrage rapide

```bash
# 1. Copier et remplir les variables d'environnement
cp .env.example .env

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer l'index Azure AI Search
python scripts/setup_index.py

# 4. Ingérer des PDFs
python scripts/ingest.py --source docs/
```

## Structure du projet

```
rag-pdf-azure/
├── .env                  # Variables d'environnement (non commité)
├── docs/                 # PDFs à ingérer (non commité)
├── scripts/
│   ├── setup_index.py    # Création de l'index Azure AI Search
│   ├── ingest.py         # Pipeline d'ingestion PDF → chunks → embeddings
│   └── query.py          # Interface de requête RAG
└── CLAUDE.md             # Contexte projet pour Claude Code
```

## Variables d'environnement

Voir `.env` pour la liste complète des variables requises.

## Workflows n8n

Les workflows sont importés via l'interface n8n. Configurer le webhook URL dans `.env`.
