"""Rebuild the FAISS index from the chunk corpus."""

from policy_intel.retrieval.vector_store import VectorStore


def main() -> None:
    store = VectorStore()
    store.build_and_save()
    print(f"Index rebuilt: {len(store.chunks)} chunks")


if __name__ == "__main__":
    main()
