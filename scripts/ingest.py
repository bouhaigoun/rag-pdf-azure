import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
import fitz  # PyMuPDF
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "rag-pdf-index")

FALLBACK_CHUNK_SIZE = 300
FALLBACK_OVERLAP = 50
MIN_WORDS_STRUCTURAL = 10  # un article court reste une unité sémantique valide
MIN_WORDS_FALLBACK = 50    # les tranches non structurées sans contexte sont ignorées

# Matches: "Article 3 - Tarification", "Clause 2 : Durée", "Section I", "Titre 4"
# ^\s* tolerates leading spaces from PDF renderers (ReportLab, etc.)
SECTION_RE = re.compile(
    r'^\s*((?:Article|Clause|Section|Titre|Chapitre)\s+\d+(?:\s*[-–:]\s*[^\n]+)?)',
    re.IGNORECASE | re.MULTILINE,
)

# Each tuple: (required_keywords, optional_keywords, doc_type)
# Match if ALL required AND ANY optional present (or no optionals defined)
DOC_TYPE_RULES = [
    (["appel", "offre"], "appel_offres"),
    (["cahier", "charge"], "cahier_charges"),
]
DOC_TYPE_SINGLE = ["contrat", "prestation", "accord", "convention"]


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_pages(pdf_path: Path) -> list[dict]:
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_doc_type(filename: str, first_text: str) -> str:
    combined = (filename + " " + first_text[:600]).lower()
    for keywords, doc_type in DOC_TYPE_RULES:
        if all(k in combined for k in keywords):
            return doc_type
    if any(k in combined for k in DOC_TYPE_SINGLE):
        return "contrat"
    return "inconnu"


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def build_page_map(pages: list[dict]) -> tuple[str, list[tuple[int, int, int]]]:
    full_text = ""
    page_map = []
    for p in pages:
        start = len(full_text)
        full_text += p["text"] + "\n\n"
        page_map.append((start, len(full_text), p["page"]))
    return full_text, page_map


def page_for_offset(offset: int, page_map: list[tuple[int, int, int]]) -> int:
    for start, end, page_num in page_map:
        if start <= offset < end:
            return page_num
    return page_map[-1][2]


def structural_chunks(full_text: str, page_map: list) -> list[dict]:
    matches = list(SECTION_RE.finditer(full_text))
    if not matches:
        return []

    chunks = []

    # Preamble before first section
    preamble = full_text[: matches[0].start()].strip()
    if len(preamble.split()) >= MIN_WORDS_STRUCTURAL:
        chunks.append({
            "content": preamble,
            "section_title": "",
            "page": page_for_offset(0, page_map),
        })

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[body_start:body_end].strip()
        content = f"{title}\n{body}".strip()

        if len(content.split()) < MIN_WORDS_STRUCTURAL:
            continue

        chunks.append({
            "content": content,
            "section_title": title,
            "page": page_for_offset(match.start(), page_map),
        })

    return chunks


def fallback_chunks(pages: list[dict]) -> list[dict]:
    chunks = []
    for page_data in pages:
        words = page_data["text"].split()
        start = 0
        while start < len(words):
            slice_words = words[start : start + FALLBACK_CHUNK_SIZE]
            if len(slice_words) >= MIN_WORDS_FALLBACK:
                chunks.append({
                    "content": " ".join(slice_words),
                    "section_title": "",
                    "page": page_data["page"],
                })
            start += FALLBACK_CHUNK_SIZE - FALLBACK_OVERLAP
    return chunks


def chunk_document(pages: list[dict]) -> tuple[list[dict], str]:
    full_text, page_map = build_page_map(pages)
    chunks = structural_chunks(full_text, page_map)
    if chunks:
        print(f"  [INFO] Structure detectee : {len(chunks)} sections")
        return chunks, "structural"
    print("  [INFO] Pas de structure detectee, fallback par mots")
    return fallback_chunks(pages), "fallback"


# ---------------------------------------------------------------------------
# Embedding & indexation
# ---------------------------------------------------------------------------

def get_embedding(text: str, max_retries: int = 6) -> list[float]:
    delay = 5
    for attempt in range(max_retries):
        response = requests.post(
            "https://api.mistral.ai/v1/embeddings",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={"model": MISTRAL_EMBED_MODEL, "input": [text]},
            timeout=30,
        )
        if response.status_code == 429:
            wait = delay * (2 ** attempt)
            print(f"    [WAIT] Rate limit 429 — attente {wait}s (tentative {attempt + 1}/{max_retries})")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    raise RuntimeError("Embedding impossible après plusieurs tentatives (rate limit persistant)")


def safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-=]", "_", value)


def ingest_pdf(pdf_path: Path) -> None:
    filename = pdf_path.name
    print(f"\n[INFO] Lecture de '{filename}'...")

    pages = extract_pages(pdf_path)
    if not pages:
        print(f"[WARN] Aucun texte extrait de '{filename}', fichier ignore.")
        return

    doc_type = detect_doc_type(filename, pages[0]["text"])
    print(f"[INFO] Type detecte : {doc_type}")

    chunks, strategy = chunk_document(pages)
    print(f"[INFO] {len(chunks)} chunks ({strategy})")

    search = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))

    for chunk_index, chunk in enumerate(chunks):
        chunk_id = safe_id(f"{filename}_{chunk['page']}_{chunk_index}")
        embedding = get_embedding(chunk["content"])
        time.sleep(0.5)

        doc = {
            "id": chunk_id,
            "content": chunk["content"],
            "filename": filename,
            "page": chunk["page"],
            "doc_type": doc_type,
            "section_title": chunk["section_title"],
            "contentVector": embedding,
        }
        search.upload_documents([doc])

        section_info = f" [{chunk['section_title']}]" if chunk["section_title"] else ""
        word_count = len(chunk["content"].split())
        print(f"  [{chunk_index + 1}] p.{chunk['page']}{section_info} | {word_count} mots -> indexe")

    print(f"\n[OK] '{filename}' : {len(chunks)} chunks indexes dans '{INDEX_NAME}'.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not all([MISTRAL_API_KEY, SEARCH_ENDPOINT, SEARCH_KEY]):
        raise ValueError("MISTRAL_API_KEY, AZURE_SEARCH_ENDPOINT et AZURE_SEARCH_KEY requis dans .env")

    if len(sys.argv) > 1:
        pdfs = [Path(sys.argv[1])]
    else:
        docs_dir = Path("docs")
        pdfs = sorted(docs_dir.glob("*.pdf"))

    if not pdfs:
        print("[ERREUR] Aucun PDF trouve dans docs/ — placez un PDF ou passez un chemin en argument.")
        sys.exit(1)

    for pdf in pdfs:
        ingest_pdf(pdf)


if __name__ == "__main__":
    main()
