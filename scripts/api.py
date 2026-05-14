import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()

MISTRAL_API_KEY    = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")
MISTRAL_CHAT_MODEL  = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
SEARCH_ENDPOINT    = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY         = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME         = os.getenv("AZURE_SEARCH_INDEX_NAME", "rag-pdf-index")
TOP_K = 3

MISTRAL_HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json",
}

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_mistral(url: str, payload: dict, max_retries: int = 6) -> dict:
    delay = 5
    for attempt in range(max_retries):
        resp = requests.post(url, headers=MISTRAL_HEADERS, json=payload, timeout=60)
        if resp.status_code == 429:
            time.sleep(delay * (2 ** attempt))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("Mistral API rate limit persistant apres plusieurs tentatives")


def get_embedding(text: str) -> list[float]:
    data = _post_mistral(
        "https://api.mistral.ai/v1/embeddings",
        {"model": MISTRAL_EMBED_MODEL, "input": [text]},
    )
    return data["data"][0]["embedding"]


def search_chunks(embedding: list[float]) -> list[dict]:
    client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
    results = client.search(
        search_text=None,
        vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=TOP_K, fields="contentVector")],
        select=["content", "filename", "page", "section_title", "doc_type"],
    )
    return [
        {
            "content":       r["content"],
            "filename":      r["filename"],
            "page":          r["page"],
            "section_title": r.get("section_title") or "",
            "doc_type":      r.get("doc_type") or "inconnu",
        }
        for r in results
    ]


def ask_mistral(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c['filename']} - page {c['page']}"
        + (f" - {c['section_title']}" if c["section_title"] else "")
        + f"]\n{c['content']}"
        for c in chunks
    )
    data = _post_mistral(
        "https://api.mistral.ai/v1/chat/completions",
        {
            "model": MISTRAL_CHAT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant juridique et technique. "
                        "Reponds en citant precisement l'article ou la clause source "
                        "avec le numero de page."
                    ),
                },
                {"role": "user", "content": f"Documents :\n{context}\n\nQuestion : {question}"},
            ],
        },
    )
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/query")
def query():
    body = request.get_json(silent=True, force=True)
    if not body or "question" not in body:
        return jsonify({"error": "Corps JSON requis avec le champ 'question'"}), 400

    question = body["question"].strip()
    if not question:
        return jsonify({"error": "Le champ 'question' ne peut pas etre vide"}), 400

    try:
        embedding = get_embedding(question)
        chunks    = search_chunks(embedding)

        if not chunks:
            return jsonify({"answer": "Aucun document pertinent trouve.", "sources": []})

        answer  = ask_mistral(question, chunks)
        sources = [
            {"file": c["filename"], "page": c["page"], "section": c["section_title"]}
            for c in chunks
        ]
        return jsonify({"answer": answer, "sources": sources})

    except requests.HTTPError as exc:
        return jsonify({"error": f"Erreur API Mistral : {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[INFO] Demarrage de l'API RAG sur http://localhost:8000")
    print("[INFO] Routes disponibles :")
    print("         GET  /health")
    print("         POST /query   { \"question\": \"...\" }")
    app.run(host="0.0.0.0", port=8000, debug=False)
