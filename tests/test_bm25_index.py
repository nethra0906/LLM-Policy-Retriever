from policy_intel.retrieval.bm25_index import BM25Index
from policy_intel.schemas import PolicyChunk


def _chunks():
    return [
        PolicyChunk(chunk_id="1", chunk_text="waiting period for cataract surgery is two years", source_doc="a.pdf"),
        PolicyChunk(chunk_id="2", chunk_text="annual leave entitlement is 20 days per year", source_doc="b.pdf"),
        PolicyChunk(chunk_id="3", chunk_text="cataract treatment exclusions and sub-limits", source_doc="a.pdf"),
    ]


def test_search_ranks_relevant_chunk_first():
    index = BM25Index(_chunks())
    results = index.search("cataract waiting period", top_k=2)
    assert results
    assert results[0][0].chunk_id == "1"


def test_search_respects_policy_filter():
    index = BM25Index(_chunks())
    results = index.search("cataract", top_k=5, policy_filter=["b.pdf"])
    assert all(chunk.source_doc == "b.pdf" for chunk, _ in results)


def test_empty_corpus_returns_no_results():
    index = BM25Index([])
    assert index.search("anything") == []
