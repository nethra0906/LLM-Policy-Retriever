from policy_intel.generation.confidence import compute_confidence
from policy_intel.schemas import PolicyChunk, RetrievedChunk


def _chunk(text="policy text"):
    return PolicyChunk(chunk_id="c1", chunk_text=text, source_doc="doc.pdf")


def test_no_candidates_yields_low_confidence():
    result = compute_confidence([])
    assert result.score == 0.0
    assert result.level == "low"


def test_strong_reranked_match_yields_high_confidence():
    candidates = [
        RetrievedChunk(chunk=_chunk(), rerank_score=8.0),
        RetrievedChunk(chunk=_chunk(), rerank_score=1.0),
        RetrievedChunk(chunk=_chunk(), rerank_score=0.5),
    ]
    result = compute_confidence(candidates)
    assert result.level == "high"
    assert 0.0 <= result.score <= 1.0


def test_weak_single_candidate_scores_lower_than_strong_match():
    strong = compute_confidence([RetrievedChunk(chunk=_chunk(), rerank_score=8.0)])
    weak = compute_confidence([RetrievedChunk(chunk=_chunk(), rerank_score=-5.0)])
    assert weak.score < strong.score


def test_falls_back_to_rrf_score_when_rerank_missing():
    candidates = [RetrievedChunk(chunk=_chunk(), rrf_score=0.03)]
    result = compute_confidence(candidates)
    assert 0.0 <= result.score <= 1.0
