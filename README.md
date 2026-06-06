# RAG Agent — Intelligent PDF Document Search

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Azure](https://img.shields.io/badge/Azure-AI_Search-blue) ![Mistral](https://img.shields.io/badge/Mistral-API-orange) ![Docker](https://img.shields.io/badge/Docker-Compose-blue) ![n8n](https://img.shields.io/badge/n8n-2.19-green)

RAG (Retrieval-Augmented Generation) pipeline for semantic search in PDF documents. Automatically index PDFs into Azure AI Search using Mistral embeddings, expose a Flask API, and orchestrate workflows via n8n.

> 185 chunks indexed · 21 PDFs (IT RFPs) · Hosted in France Central (GDPR compliant)

## Tech Stack

| Component | Role |
|-----------|------|
| Azure AI Search | HNSW vector index — 1024 dimensions |
| Azure Blob Storage | PDF source storage |
| Mistral API | Embeddings (`mistral-embed`) + generation (`mistral-large`) |
| Flask API | `/query` endpoint — REST interface |
| n8n | Ingestion and query workflow orchestration |
| Docker Compose | Production deployment (n8n + Flask API) |

## Architecture
INGESTION
PDF upload
│
▼
Azure Blob Storage
│
▼  (n8n workflow)
Chunking (paragraphs)
│
▼
Mistral Embeddings (mistral-embed, 1024 dims)
│
▼
Azure AI Search Index
QUERY
User question
│
▼
Flask API /query
├── Query embedding (mistral-embed)
├── Vector search Azure AI Search (top-k chunks)
├── Enriched prompt (context + question)
└── Mistral LLM (mistral-large) → Answer + citations
## Getting Started

### Prerequisites
- Docker and Docker Compose
- Azure account (AI Search + Blob Storage active)
- Mistral API key

### 1. Environment Variables
```bash
cp .env.example .env
```

Fill in `.env`:
Azure
AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
AZURE_SEARCH_KEY=<admin-key>
AZURE_SEARCH_INDEX=rag-pdf-index
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_CONTAINER_NAME=pdfs
Mistral
MISTRAL_API_KEY=<api-key>
n8n
N8N_WEBHOOK_URL=http://n8n:5678/webhook/rag-query
### 2. Start with Docker Compose
```bash
docker compose up -d
```
Starts:
- Flask API on `http://localhost:5000`
- n8n on `http://localhost:5678`

### 3. Create Azure AI Search Index
```bash
python scripts/setup_index.py
```

### 4. Ingest PDFs
Drop PDFs in `docs/`, then:
```bash
python scripts/ingest.py --source docs/
```

### 5. Import n8n Workflow
In n8n UI (`http://localhost:5678`), import `workflow_n8n.json`.

## Usage

### REST API
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the technical requirements for IT RFPs?"}'
```

Response:
```json
{
  "answer": "Technical requirements include...",
  "sources": [
    { "filename": "ao_007.pdf", "chunk": "...", "score": 0.94 }
  ]
}
```

### CLI
```bash
python scripts/query.py "What are the cybersecurity requirements?"
```

## Project Structure
rag-pdf-azure/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── workflow_n8n.json
├── .env.example
├── docs/
└── scripts/
├── api.py
├── setup_index.py
├── setup_azure.py
├── ingest.py
├── query.py
└── create_n8n_workflow.py
## Data & Compliance

| Parameter | Value |
|-----------|-------|
| Azure Region | France Central |
| Indexed documents | 21 PDFs (IT RFPs) |
| Chunks | 185 |
| Embedding model | `mistral-embed` (1024 dims) |
| LLM model | `mistral-large` |
| Compliance | GDPR — data hosted in France |