"""Data models for retrieval and generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyChunk:
    chunk_id: str
    chunk_text: str
    source_doc: str
    page_no: int | None = None
    clause_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyChunk:
        return cls(
            chunk_id=data.get("chunk_id", ""),
            chunk_text=data.get("chunk_text", ""),
            source_doc=data.get("source_doc", "unknown"),
            page_no=data.get("page_no"),
            clause_id=data.get("clause_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "chunk_text": self.chunk_text,
            "source_doc": self.source_doc,
            "page_no": self.page_no,
            "clause_id": self.clause_id,
        }

    def citation_label(self) -> str:
        page = f"p.{self.page_no}" if self.page_no is not None else "p.?"
        clause = f", clause {self.clause_id}" if self.clause_id else ""
        return f"{self.source_doc} ({page}{clause})"


@dataclass
class RetrievedChunk:
    chunk: PolicyChunk
    vector_score: float = 0.0
    bm25_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float | None = None

    def to_citation_dict(self) -> dict[str, Any]:
        return {
            "source_doc": self.chunk.source_doc,
            "page_no": self.chunk.page_no,
            "clause_id": self.chunk.clause_id,
            "label": self.chunk.citation_label(),
            "excerpt": self.chunk.chunk_text[:300],
            "rerank_score": self.rerank_score,
            "rrf_score": round(self.rrf_score, 4),
        }


@dataclass
class ConfidenceResult:
    score: float
    level: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 3),
            "level": self.level,
            "rationale": self.rationale,
        }


@dataclass
class QueryResult:
    question: str
    answer: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    confidence: ConfidenceResult | None = None
    retrieved_count: int = 0
    policies_searched: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "question": self.question,
            "answer": self.answer,
            "citations": self.citations,
            "retrieved_count": self.retrieved_count,
            "policies_searched": self.policies_searched,
        }
        if self.confidence:
            payload["confidence"] = self.confidence.to_dict()
        return payload
