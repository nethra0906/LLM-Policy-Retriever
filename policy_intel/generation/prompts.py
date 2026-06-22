"""Prompt templates for HackRx compatibility and platform Q&A."""

from policy_intel.schemas import RetrievedChunk


def format_context(chunks: list[RetrievedChunk]) -> str:
    sections: list[str] = []
    for idx, item in enumerate(chunks, start=1):
        chunk = item.chunk
        header = (
            f"[Source {idx}] Document: {chunk.source_doc} | "
            f"Page: {chunk.page_no} | Clause: {chunk.clause_id}"
        )
        sections.append(f"{header}\n{chunk.chunk_text}")
    return "\n\n".join(sections)


def hackrx_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    """One-sentence answer prompt — preserves HackRx API behavior."""
    context = format_context(chunks)
    return f"""You are an insurance policy analyst. Answer using ONLY the excerpts below.
Respond in exactly one clear sentence. No bullet points, no preamble.

--- POLICY EXCERPTS ---
{context}

--- QUESTION ---
{query}

Answer:"""


def platform_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    """Grounded answer with explainability for the enterprise UI."""
    context = format_context(chunks)
    return f"""You are an enterprise Policy Intelligence assistant for insurance documents.

Rules:
1. Answer ONLY from the provided policy excerpts.
2. If the answer is not in the excerpts, say: "The provided policy excerpts do not contain enough information to answer this question."
3. Be precise about conditions, waiting periods, limits, and exclusions.
4. Reference source numbers [Source N] when stating specific facts.
5. Keep the answer concise (2-4 sentences) but include key qualifying conditions.

--- POLICY EXCERPTS ---
{context}

--- QUESTION ---
{query}

Answer:"""
