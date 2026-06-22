"""End-to-end policy Q&A orchestration."""

from __future__ import annotations

from typing import Sequence

from policy_intel.config import CONTEXT_TOP_K, HYBRID_CANDIDATE_K
from policy_intel.generation.confidence import compute_confidence
from policy_intel.generation.generator import AnswerGenerator
from policy_intel.ingestion.pdf_loader import extract_chunks_from_pdf_url
from policy_intel.logging_config import setup_logging
from policy_intel.retrieval.bm25_index import BM25Index
from policy_intel.retrieval.hybrid_retriever import HybridRetriever
from policy_intel.retrieval.reranker import Reranker
from policy_intel.retrieval.vector_store import EphemeralVectorStore, VectorStore
from policy_intel.schemas import PolicyChunk, QueryResult, RetrievedChunk

logger = setup_logging()


class PolicyPipeline:
    """
    Unified retrieval-augmented generation pipeline.

    Supports:
    - Static multi-policy corpus (hybrid + rerank)
    - Dynamic PDF URL ingestion
    - Policy filtering
    - Citations and confidence scoring
    """

    def __init__(self) -> None:
        logger.info("Initializing Policy Intelligence pipeline...")
        self.vector_store = VectorStore()
        self.bm25_index = BM25Index(self.vector_store.chunks)
        self.hybrid_retriever = HybridRetriever(self.vector_store, self.bm25_index)
        self.reranker = Reranker()
        self._generator = None
        logger.info("Pipeline ready (%d policy chunks indexed)", len(self.vector_store.chunks))

    @property
    def generator(self):
        if self._generator is None:
            from policy_intel.generation.generator import AnswerGenerator

            self._generator = AnswerGenerator()
        return self._generator

    def list_policies(self) -> list[dict[str, str | int]]:
        return self.vector_store.list_policies()

    def _retrieve(
        self,
        query: str,
        retriever: HybridRetriever,
        policy_filter: Sequence[str] | None = None,
    ) -> list[RetrievedChunk]:
        candidates = retriever.retrieve(
            query,
            top_k=HYBRID_CANDIDATE_K,
            policy_filter=policy_filter,
        )
        reranked = self.reranker.rerank(query, candidates)
        return reranked[:CONTEXT_TOP_K]

    def query_static(
        self,
        question: str,
        policy_filter: Sequence[str] | None = None,
        mode: str = "platform",
    ) -> QueryResult:
        policies = list(policy_filter) if policy_filter else [
            p["id"] for p in self.list_policies()
        ]
        chunks = self._retrieve(question, self.hybrid_retriever, policy_filter)

        if mode == "hackrx":
            answer = self.generator.generate_hackrx(question, chunks)
        else:
            answer = self.generator.generate_platform(question, chunks)

        confidence = compute_confidence(chunks)
        return QueryResult(
            question=question,
            answer=answer,
            citations=[c.to_citation_dict() for c in chunks],
            confidence=confidence,
            retrieved_count=len(chunks),
            policies_searched=policies if policy_filter else ["all"],
        )

    def query_dynamic(
        self,
        question: str,
        pdf_url: str,
        mode: str = "platform",
    ) -> QueryResult:
        dynamic_chunks = extract_chunks_from_pdf_url(pdf_url)
        ephemeral_store = EphemeralVectorStore(dynamic_chunks, self.vector_store.embedder)
        bm25 = BM25Index(dynamic_chunks)
        retriever = HybridRetriever(ephemeral_store, bm25)
        chunks = self._retrieve(question, retriever)

        if mode == "hackrx":
            answer = self.generator.generate_hackrx(question, chunks)
        else:
            answer = self.generator.generate_platform(question, chunks)

        confidence = compute_confidence(chunks)
        source_doc = dynamic_chunks[0].source_doc if dynamic_chunks else pdf_url
        return QueryResult(
            question=question,
            answer=answer,
            citations=[c.to_citation_dict() for c in chunks],
            confidence=confidence,
            retrieved_count=len(chunks),
            policies_searched=[source_doc],
        )

    def query_batch(
        self,
        questions: list[str],
        pdf_url: str | None = None,
        policy_filter: Sequence[str] | None = None,
        mode: str = "platform",
    ) -> list[QueryResult]:
        if pdf_url:
            dynamic_chunks = extract_chunks_from_pdf_url(pdf_url)
            ephemeral_store = EphemeralVectorStore(dynamic_chunks, self.vector_store.embedder)
            bm25 = BM25Index(dynamic_chunks)
            retriever = HybridRetriever(ephemeral_store, bm25)
            source_doc = dynamic_chunks[0].source_doc if dynamic_chunks else pdf_url

            results: list[QueryResult] = []
            for question in questions:
                chunks = self._retrieve(question, retriever)
                answer = (
                    self.generator.generate_hackrx(question, chunks)
                    if mode == "hackrx"
                    else self.generator.generate_platform(question, chunks)
                )
                results.append(
                    QueryResult(
                        question=question,
                        answer=answer,
                        citations=[c.to_citation_dict() for c in chunks],
                        confidence=compute_confidence(chunks),
                        retrieved_count=len(chunks),
                        policies_searched=[source_doc],
                    )
                )
            return results

        return [
            self.query_static(q, policy_filter=policy_filter, mode=mode)
            for q in questions
        ]
