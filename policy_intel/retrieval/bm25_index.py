"""BM25 lexical retrieval for hybrid search."""

from __future__ import annotations

from typing import Sequence

from rank_bm25 import BM25Okapi

from policy_intel.schemas import PolicyChunk


class BM25Index:
    """Lightweight in-memory BM25 index over policy chunks."""

    def __init__(self, chunks: list[PolicyChunk]) -> None:
        self.chunks = chunks
        self._chunk_indices = list(range(len(chunks)))
        tokenized = [self._tokenize(chunk.chunk_text) for chunk in chunks]
        self._bm25 = BM25Okapi(tokenized)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 20,
        policy_filter: Sequence[str] | None = None,
    ) -> list[tuple[PolicyChunk, float]]:
        if not self.chunks:
            return []

        scores = self._bm25.get_scores(self._tokenize(query))
        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        allowed = set(policy_filter) if policy_filter else None
        results: list[tuple[PolicyChunk, float]] = []

        for idx, score in ranked:
            chunk = self.chunks[idx]
            if allowed is not None and chunk.source_doc not in allowed:
                continue
            results.append((chunk, float(score)))
            if len(results) >= top_k:
                break

        return results
