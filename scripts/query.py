import os
import sys
import time

import requests
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")
MISTRAL_CHAT_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "rag-pdf-index")

TOP_K = 3
MISTRAL_HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json",
}


def _post_with_retry(url: str, payload: dict, max_retries: int = 6) -> dict:
    delay = 5
    for attempt in range(max_retries):
        response = requests.post(url, headers=MISTRAL_HEADERS, json=payload, timeout=60)
        if response.status_code == 429:
            wait = delay * (2 ** attempt)
            print(f"  [WAIT] Rate limit 429 — attente {wait}s (tentative {attempt + 1}/{max_retries})")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("API Mistral indisponible apres plusieurs tentatives (rate limit persistant)")


def get_embedding(text: str) -> list[float]:
    data = _post_with_retry(
        "https://api.mistral.ai/v1/embeddings",
        {"model": MISTRAL_EMBED_MODEL, "input": [text]},
    )
    return data["data"][0]["embedding"]


def search_chunks(embedding: list[float]) -> list[dict]:
    client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=TOP_K,
        fields="contentVector",
    )
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["content", "filename", "page", "section_title", "doc_type"],
    )
    return [
        {
            "content": r["content"],
            "filename": r["filename"],
            "page": r["page"],
            "section_title": r.get("section_title") or "",
            "doc_type": r.get("doc_type") or "inconnu",
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
    data = _post_with_retry(
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
                {
                    "role": "user",
                    "content": f"Documents :\n{context}\n\nQuestion : {question}",
                },
            ],
        },
    )
    return data["choices"][0]["message"]["content"]


def main() -> None:
    if not all([MISTRAL_API_KEY, SEARCH_ENDPOINT, SEARCH_KEY]):
        raise ValueError("MISTRAL_API_KEY, AZURE_SEARCH_ENDPOINT et AZURE_SEARCH_KEY requis dans .env")

    if len(sys.argv) < 2:
        print("Usage : python scripts/query.py \"<question>\"")
        sys.exit(1)

    question = sys.argv[1]
    print(f"[INFO] Question : {question}")

    print("[INFO] Embedding de la question...")
    embedding = get_embedding(question)

    print(f"[INFO] Recherche des {TOP_K} chunks les plus proches...")
    chunks = search_chunks(embedding)
    if not chunks:
        print("[WARN] Aucun chunk trouve dans l'index.")
        sys.exit(0)

    for i, c in enumerate(chunks, 1):
        section = f" | {c['section_title']}" if c["section_title"] else ""
        print(f"  [{i}] {c['filename']} p.{c['page']}{section} - {len(c['content'].split())} mots")

    print("\n[INFO] Generation de la reponse...\n")
    answer = ask_mistral(question, chunks)
    print(answer)


if __name__ == "__main__":
    main()
