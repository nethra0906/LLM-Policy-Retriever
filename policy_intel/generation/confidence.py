"""Retrieval-grounded confidence scoring."""

from __future__ import annotations

import math

from policy_intel.schemas import ConfidenceResult, RetrievedChunk


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def compute_confidence(candidates: list[RetrievedChunk]) -> ConfidenceResult:
    """
    Estimate answer confidence from reranker scores and retrieval separation.

    Uses only local signals — no extra LLM call (fast, RAM-friendly).
    """
    if not candidates:
        return ConfidenceResult(
            score=0.0,
            level="low",
            rationale="No relevant policy excerpts were retrieved.",
        )

    rerank_scores = [
        c.rerank_score for c in candidates if c.rerank_score is not None
    ]
    if not rerank_scores:
        rerank_scores = [c.rrf_score for c in candidates]

    top_score = rerank_scores[0]
    second_score = rerank_scores[1] if len(rerank_scores) > 1 else rerank_scores[0] * 0.5
    margin = max(top_score - second_score, 0.0)

    # Cross-encoder scores typically range ~ -10 to +10; RRF scores are smaller.
    if any(c.rerank_score is not None for c in candidates):
        relevance = _sigmoid(top_score)
        margin_component = min(margin / 4.0, 1.0)
    else:
        relevance = min(top_score * 8.0, 1.0)
        margin_component = min(margin * 15.0, 1.0)

    coverage = min(len(candidates) / 3.0, 1.0)
    score = 0.55 * relevance + 0.30 * margin_component + 0.15 * coverage
    score = round(min(max(score, 0.0), 1.0), 3)

    if score >= 0.75:
        level = "high"
    elif score >= 0.50:
        level = "medium"
    else:
        level = "low"

    rationale = (
        f"Top retrieval score={top_score:.2f}, margin over next={margin:.2f}, "
        f"sources={len(candidates)}."
    )
    return ConfidenceResult(score=score, level=level, rationale=rationale)
