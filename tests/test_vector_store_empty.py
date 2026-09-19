import numpy as np

from policy_intel.retrieval.vector_store import EphemeralVectorStore


class _FakeEmbedder:
    """Minimal stand-in for SentenceTransformer.encode, no model download needed."""

    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        return np.zeros((len(texts), 4), dtype=np.float32)


def test_ephemeral_store_handles_empty_chunks_without_crashing():
    store = EphemeralVectorStore([], _FakeEmbedder())
    assert store.index is None
    assert store.search("anything") == []
