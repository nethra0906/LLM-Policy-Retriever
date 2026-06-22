"""PDF ingestion with metadata-aware chunking."""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

import pdfplumber
import requests

from policy_intel.config import DYNAMIC_CHUNK_OVERLAP, DYNAMIC_CHUNK_WORDS
from policy_intel.schemas import PolicyChunk


def extract_chunks_from_pdf_path(
    pdf_path: str | Path,
    source_doc: str | None = None,
) -> list[PolicyChunk]:
    """Extract page-aware paragraph chunks from a local PDF file."""
    pdf_path = Path(pdf_path)
    doc_name = source_doc or pdf_path.name
    chunks: list[PolicyChunk] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text or not text.strip():
                continue

            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if len(paragraphs) <= 1:
                paragraphs = _word_window_chunks(text)

            for idx, paragraph in enumerate(paragraphs):
                chunks.append(
                    PolicyChunk(
                        chunk_id=str(uuid.uuid4()),
                        chunk_text=paragraph,
                        source_doc=doc_name,
                        page_no=page_number,
                        clause_id=f"{page_number}-{idx}",
                    )
                )

    return chunks


def extract_chunks_from_pdf_url(pdf_url: str) -> list[PolicyChunk]:
    """Download a PDF from URL and return metadata-rich chunks."""
    response = requests.get(pdf_url, timeout=120)
    response.raise_for_status()

    source_doc = pdf_url.split("?")[0].rstrip("/").split("/")[-1] or "uploaded_policy.pdf"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        return extract_chunks_from_pdf_path(tmp_path, source_doc=source_doc)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _word_window_chunks(text: str) -> list[str]:
    """Fallback fixed-size word windows with overlap for dense PDF layouts."""
    words = text.split()
    if not words:
        return []

    step = max(DYNAMIC_CHUNK_WORDS - DYNAMIC_CHUNK_OVERLAP, 1)
    windows: list[str] = []
    for start in range(0, len(words), step):
        window = " ".join(words[start : start + DYNAMIC_CHUNK_WORDS])
        if window.strip():
            windows.append(window)
    return windows
