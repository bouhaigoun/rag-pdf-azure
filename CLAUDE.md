# CLAUDE.md — RAG PDF Azure

## Contexte projet

Pipeline RAG (Retrieval-Augmented Generation) pour indexer des PDFs et répondre à des questions en langage naturel. Orchestré via **n8n**, avec stockage sur **Azure Blob Storage**, indexation dans **Azure AI Search**, et génération via **Mistral API**.

## Stack technique

- **Azure Blob Storage** : stockage des PDFs bruts uploadés
- **Azure AI Search** : index vectoriel avec recherche hybride (keyword + sémantique)
- **Mistral API** : `mistral-embed` pour les embeddings, `mistral-large-latest` pour la génération
- **n8n** : orchestration des workflows d'ingestion et de requête (webhooks, nœuds HTTP)
- **Python** : scripts d'ingestion, chunking, appels API

## Architecture des données

1. PDF uploadé dans Azure Blob Storage
2. n8n déclenche le pipeline d'ingestion
3. Extraction texte → chunking (≈1000 tokens, overlap 200)
4. Embeddings via `mistral-embed` (dimension 1024)
5. Indexation dans Azure AI Search (champ `contentVector`)
6. À la requête : embed la question → recherche top-k → prompt Mistral → réponse

## Conventions de code

- Python 3.11+
- Variables d'env chargées via `python-dotenv`
- Pas de credentials hardcodés — toujours via `.env`
- Logs structurés (niveau configuré via `LOG_LEVEL`)
- Chunks nommés `{blob_name}_{chunk_index}` pour la traçabilité

## Fichiers clés

- `.env` : toutes les credentials et paramètres (ne jamais committer)
- `docs/` : PDFs sources (ne jamais committer)
- `scripts/setup_index.py` : création/recréation de l'index Azure AI Search
- `scripts/ingest.py` : pipeline complet PDF → Azure AI Search
- `scripts/query.py` : RAG query end-to-end

## Points d'attention

- L'index Azure AI Search doit avoir un champ `contentVector` de type `Collection(Edm.Single)` avec dimension 1024
- Mistral `mistral-embed` retourne des vecteurs de dimension 1024
- n8n tourne en local ou sur VM Azure — configurer `N8N_WEBHOOK_URL` en conséquence
- Les PDFs dans `docs/` sont exclus du git (données potentiellement sensibles)
