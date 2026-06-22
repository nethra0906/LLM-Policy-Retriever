"""FAISS vector store with normalized embeddings."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Sequence

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from policy_intel.config import (
    CHUNKS_PATH,
    EMBED_MODEL,
    INDEX_PATH,
    METADATA_PATH,
)
from policy_intel.logging_config import setup_logging
from policy_intel.schemas import PolicyChunk

logger = setup_logging()


class VectorStore:
    """Persistent FAISS index backed by normalized dense embeddings."""

    def __init__(self, embedder: SentenceTransformer | None = None) -> None:
        self.embedder = embedder or SentenceTransformer(EMBED_MODEL)
        self.chunks: list[PolicyChunk] = []
        self.index: faiss.Index | None = None
        self._embeddings: np.ndarray | None = None
        self._load_or_build()

    def _load_or_build(self) -> None:
        if INDEX_PATH.exists() and METADATA_PATH.exists():
            try:
                self._load_index()
                if isinstance(self.index, faiss.IndexFlatIP):
                    logger.info("Loaded FAISS index with %d chunks", len(self.chunks))
                    return
                logger.info("Migrating legacy FAISS index to normalized cosine (IndexFlatIP).")
            except Exception as exc:
                logger.warning("Failed to load index (%s); rebuilding.", exc)

        if not CHUNKS_PATH.exists():
            raise FileNotFoundError(f"Chunk corpus not found at {CHUNKS_PATH}")

        raw_chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        self.chunks = [PolicyChunk.from_dict(c) for c in raw_chunks]
        self.build_and_save()

    def _load_index(self) -> None:
        with open(METADATA_PATH, "rb") as handle:
            raw_metadata = pickle.load(handle)

        self.chunks = [PolicyChunk.from_dict(c) for c in raw_metadata]
        self.index = faiss.read_index(str(INDEX_PATH))

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                f"Index size ({self.index.ntotal}) != metadata ({len(self.chunks)})"
            )

    def build_and_save(self) -> None:
        texts = [chunk.chunk_text for chunk in self.chunks]
        embeddings = self._encode(texts)
        self._embeddings = embeddings

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype(np.float32))

        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(METADATA_PATH, "wb") as handle:
            pickle.dump([c.to_dict() for c in self.chunks], handle)

        logger.info("Built and saved FAISS index (%d vectors)", len(self.chunks))

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return (vectors / norms).astype(np.float32)

    def list_policies(self) -> list[dict[str, str | int]]:
        counts: dict[str, int] = {}
        for chunk in self.chunks:
            counts[chunk.source_doc] = counts.get(chunk.source_doc, 0) + 1

        return [
            {"id": doc, "name": doc, "chunk_count": count}
            for doc, count in sorted(counts.items(), key=lambda item: item[0])
        ]

    def _candidate_indices(self, policy_filter: Sequence[str] | None) -> list[int]:
        if not policy_filter:
            return list(range(len(self.chunks)))

        allowed = set(policy_filter)
        return [i for i, chunk in enumerate(self.chunks) if chunk.source_doc in allowed]

    def search(
        self,
        query: str,
        top_k: int = 20,
        policy_filter: Sequence[str] | None = None,
    ) -> list[tuple[PolicyChunk, float]]:
        if self.index is None:
            raise RuntimeError("Vector index is not initialized")

        candidate_indices = self._candidate_indices(policy_filter)
        if not candidate_indices:
            return []

        query_vector = self._encode([query])[0]
        search_k = min(max(top_k * 3, top_k), len(self.chunks))
        scores, indices = self.index.search(query_vector.reshape(1, -1), search_k)

        results: list[tuple[PolicyChunk, float]] = []
        allowed = set(candidate_indices)
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx not in allowed:
                continue
            results.append((self.chunks[idx], float(score)))
            if len(results) >= top_k:
                break

        return results


class EphemeralVectorStore:
    """In-memory vector index for dynamically ingested documents."""

    def __init__(self, chunks: list[PolicyChunk], embedder: SentenceTransformer) -> None:
        self.chunks = chunks
        self.embedder = embedder
        texts = [chunk.chunk_text for chunk in chunks]
        vectors = self._encode(texts)

        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors.astype(np.float32))

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return (vectors / norms).astype(np.float32)

    def search(self, query: str, top_k: int = 20) -> list[tuple[PolicyChunk, float]]:
        if not self.chunks:
            return []

        query_vector = self._encode([query])[0]
        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_vector.reshape(1, -1), k)

        results: list[tuple[PolicyChunk, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self.chunks[idx], float(score)))
        return results
