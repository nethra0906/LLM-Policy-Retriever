"""Central configuration for the Policy Intelligence Platform."""

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Embedding & retrieval
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L12-v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
CHUNKS_PATH = ROOT_DIR / "chunks" / "all_policy_chunks.json"
INDEX_DIR = ROOT_DIR / "better_embeddings" / "embeddings"
INDEX_PATH = INDEX_DIR / "chunks.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"

# Gemini
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Retrieval tuning (optimized for 16 GB RAM laptops)
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "20"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "20"))
HYBRID_CANDIDATE_K = int(os.getenv("HYBRID_CANDIDATE_K", "25"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "5"))
CONTEXT_TOP_K = int(os.getenv("CONTEXT_TOP_K", "3"))
RRF_K = int(os.getenv("RRF_K", "60"))

# Feature flags
ENABLE_RERANKING = os.getenv("ENABLE_RERANKING", "true").lower() == "true"
ENABLE_HYBRID = os.getenv("ENABLE_HYBRID", "true").lower() == "true"

# Dynamic PDF chunking
DYNAMIC_CHUNK_WORDS = int(os.getenv("DYNAMIC_CHUNK_WORDS", "200"))
DYNAMIC_CHUNK_OVERLAP = int(os.getenv("DYNAMIC_CHUNK_OVERLAP", "40"))
