import numpy as np
from sentence_transformers import SentenceTransformer

from policy_intel.retrieval.vector_store import VectorStore


def load_index_and_metadata():
    store = VectorStore()
    return store.index, [c.to_dict() for c in store.chunks]


def encode_query(query, model_name="all-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    embedding = model.encode([query], convert_to_numpy=True)[0]
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.astype(np.float32)


def search_index(query_embedding, index, metadata, top_k=5):
    scores, indices = index.search(np.array([query_embedding]), k=top_k)
    return [metadata[i] for i in indices[0] if i >= 0]


def main():
    query = "Are there any sub-limits on room rent and ICU charges for Plan A?"
    index, metadata = load_index_and_metadata()
    query_embedding = encode_query(query)
    top_chunks = search_index(query_embedding, index, metadata, top_k=5)

    print("\nTop matching chunks:")
    for i, chunk in enumerate(top_chunks):
        print(f"\n--- Result {i + 1} ---")
        print(f"Clause ID: {chunk.get('clause_id')}")
        print(f"Source Doc: {chunk.get('source_doc')}")
        print(f"Page No: {chunk.get('page_no')}")
        print(f"Text:\n{chunk.get('chunk_text', '')[:500]}...\n")


if __name__ == "__main__":
    main()
