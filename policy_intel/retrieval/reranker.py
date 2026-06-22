"""Cross-encoder reranking (lazy-loaded for memory efficiency)."""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from policy_intel.config import ENABLE_RERANKING, RERANK_MODEL, RERANK_TOP_K
from policy_intel.logging_config import setup_logging
from policy_intel.schemas import RetrievedChunk

logger = setup_logging()

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        logger.info("Loading cross-encoder reranker: %s", RERANK_MODEL)
        _reranker = CrossEncoder(RERANK_MODEL)
    return _reranker


class Reranker:
    """Re-score hybrid candidates with a lightweight cross-encoder."""

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = RERANK_TOP_K,
    ) -> list[RetrievedChunk]:
        if not candidates:
            return []

        if not ENABLE_RERANKING or len(candidates) == 1:
            for candidate in candidates:
                candidate.rerank_score = candidate.rrf_score
            return candidates[:top_k]

        model = get_reranker()
        pairs = [(query, candidate.chunk.chunk_text) for candidate in candidates]
        scores = model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate.rerank_score = float(score)

        ranked = sorted(
            candidates,
            key=lambda item: item.rerank_score if item.rerank_score is not None else 0.0,
            reverse=True,
        )
        return ranked[:top_k]
