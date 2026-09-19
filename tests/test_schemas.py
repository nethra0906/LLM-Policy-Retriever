from policy_intel.schemas import PolicyChunk, RetrievedChunk


def test_policy_chunk_from_dict_defaults_missing_fields():
    chunk = PolicyChunk.from_dict({"chunk_text": "hello"})
    assert chunk.chunk_id == ""
    assert chunk.source_doc == "unknown"
    assert chunk.page_no is None
    assert chunk.clause_id is None


def test_policy_chunk_round_trips_through_dict():
    original = PolicyChunk(
        chunk_id="c1",
        chunk_text="Some clause text",
        source_doc="policy.pdf",
        page_no=3,
        clause_id="3-1",
    )
    restored = PolicyChunk.from_dict(original.to_dict())
    assert restored == original


def test_citation_label_formats_page_and_clause():
    chunk = PolicyChunk(chunk_id="c1", chunk_text="x", source_doc="doc.pdf", page_no=2, clause_id="2-0")
    assert chunk.citation_label() == "doc.pdf (p.2, clause 2-0)"


def test_citation_label_handles_missing_page_and_clause():
    chunk = PolicyChunk(chunk_id="c1", chunk_text="x", source_doc="doc.pdf")
    assert chunk.citation_label() == "doc.pdf (p.?)"


def test_retrieved_chunk_citation_dict_truncates_excerpt():
    chunk = PolicyChunk(chunk_id="c1", chunk_text="x" * 500, source_doc="doc.pdf")
    retrieved = RetrievedChunk(chunk=chunk, rrf_score=0.5)
    citation = retrieved.to_citation_dict()
    assert len(citation["excerpt"]) == 300
    assert citation["rrf_score"] == 0.5
