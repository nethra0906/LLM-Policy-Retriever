"""PDF ingestion with metadata-aware chunking."""

from __future__ import annotations

import ipaddress
import os
import socket
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse

import pdfplumber
import requests

from policy_intel.config import DYNAMIC_CHUNK_OVERLAP, DYNAMIC_CHUNK_WORDS
from policy_intel.schemas import PolicyChunk

MAX_PDF_BYTES = 50 * 1024 * 1024


class UnsafePdfUrlError(ValueError):
    """Raised when a caller-supplied PDF URL targets a disallowed destination."""


def _assert_public_url(pdf_url: str) -> None:
    """Block SSRF: only allow http(s) URLs resolving to public IP addresses.

    Guards against the /api/v1/query and /hackrx/run endpoints being used to
    make the server fetch internal services, loopback, link-local, or cloud
    metadata addresses (e.g. 169.254.169.254) via an attacker-supplied URL.
    """
    parsed = urlparse(pdf_url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafePdfUrlError(f"Unsupported URL scheme: {parsed.scheme!r}")
    if not parsed.hostname:
        raise UnsafePdfUrlError("URL is missing a hostname")

    try:
        addrinfo = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise UnsafePdfUrlError(f"Could not resolve host: {parsed.hostname}") from exc

    for family, *_rest, sockaddr in addrinfo:
        ip = ipaddress.ip_address(sockaddr[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise UnsafePdfUrlError(
                f"URL resolves to a disallowed address: {ip}"
            )


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
    _assert_public_url(pdf_url)

    response = requests.get(pdf_url, timeout=120, stream=True, allow_redirects=False)
    response.raise_for_status()

    source_doc = pdf_url.split("?")[0].rstrip("/").split("/")[-1] or "uploaded_policy.pdf"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
        downloaded = 0
        for block in response.iter_content(chunk_size=1024 * 256):
            downloaded += len(block)
            if downloaded > MAX_PDF_BYTES:
                raise ValueError(f"PDF exceeds maximum allowed size of {MAX_PDF_BYTES} bytes")
            tmp.write(block)

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
