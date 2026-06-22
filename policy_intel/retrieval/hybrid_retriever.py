"""Reciprocal Rank Fusion hybrid retriever."""

from __future__ import annotations

from typing import Protocol, Sequence

from policy_intel.config import BM25_TOP_K, ENABLE_HYBRID, RRF_K, VECTOR_TOP_K
from policy_intel.schemas import PolicyChunk, RetrievedChunk


class VectorSearcher(Protocol):
    def search(
        self,
        query: str,
        top_k: int = 20,
        policy_filter: Sequence[str] | None = None,
    ) -> list[tuple[PolicyChunk, float]]: ...


class BM25Searcher(Protocol):
    def search(
        self,
        query: str,
        top_k: int = 20,
        policy_filter: Sequence[str] | None = None,
    ) -> list[tuple[PolicyChunk, float]]: ...


class HybridRetriever:
    """Combine dense vector and BM25 retrieval via Reciprocal Rank Fusion."""

    def __init__(
        self,
        vector_store: VectorSearcher,
        bm25_index: BM25Searcher | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.bm25_index = bm25_index

    def retrieve(
        self,
        query: str,
        top_k: int = 25,
        policy_filter: Sequence[str] | None = None,
    ) -> list[RetrievedChunk]:
        vector_hits = self.vector_store.search(
            query,
            top_k=VECTOR_TOP_K,
            policy_filter=policy_filter,
        )

        bm25_hits: list[tuple[PolicyChunk, float]] = []
        if ENABLE_HYBRID and self.bm25_index is not None:
            bm25_hits = self.bm25_index.search(
                query,
                top_k=BM25_TOP_K,
                policy_filter=policy_filter,
            )

        if not bm25_hits:
            return [
                RetrievedChunk(chunk=chunk, vector_score=score, rrf_score=score)
                for chunk, score in vector_hits[:top_k]
            ]

        fused: dict[str, RetrievedChunk] = {}

        for rank, (chunk, score) in enumerate(vector_hits):
            key = chunk.chunk_id or f"{chunk.source_doc}:{chunk.clause_id}"
            entry = fused.setdefault(
                key,
                RetrievedChunk(chunk=chunk, vector_score=score),
            )
            entry.rrf_score += 1.0 / (RRF_K + rank + 1)
            entry.vector_score = max(entry.vector_score, score)

        for rank, (chunk, score) in enumerate(bm25_hits):
            key = chunk.chunk_id or f"{chunk.source_doc}:{chunk.clause_id}"
            entry = fused.setdefault(
                key,
                RetrievedChunk(chunk=chunk, bm25_score=score),
            )
            entry.rrf_score += 1.0 / (RRF_K + rank + 1)
            entry.bm25_score = max(entry.bm25_score, score)

        ranked = sorted(fused.values(), key=lambda item: item.rrf_score, reverse=True)
        return ranked[:top_k]
