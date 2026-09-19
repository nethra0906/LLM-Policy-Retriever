# 📋 Policy Intelligence Platform

A retrieval-augmented Q&A system for insurance policy documents. It combines dense
vector search, BM25 lexical search, cross-encoder reranking, and Gemini-based
generation to answer natural-language questions with grounded citations and a
confidence score — over a static indexed corpus or a PDF supplied at query time.

---

## Architecture

```text
                         User Question
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
          Dense retrieval           BM25 lexical search
        (FAISS + MiniLM-L12)         (rank-bm25)
                 │                         │
                 └──────────┬──────────────┘
                             ▼
                Reciprocal Rank Fusion (RRF)
                             │
                             ▼
              Cross-encoder reranking (top-K)
                             │
                             ▼
                  Gemini answer generation
                  (grounded on retrieved chunks)
                             │
                             ▼
        Answer + citations + confidence score
```

- **Static corpus**: pre-chunked policy PDFs are embedded once and served from a
  persistent FAISS index (`better_embeddings/embeddings/`).
- **Dynamic ingestion**: a PDF URL supplied in a request is downloaded, chunked,
  and indexed in memory for that request only (nothing is persisted).
- **Confidence scoring**: derived entirely from local retrieval signals (reranker
  score, score margin, number of supporting chunks) — no extra LLM call.

---

## Project Structure

```text
policy_intel/
├── config.py                # env-driven configuration
├── pipeline.py               # orchestrates retrieval → rerank → generation
├── schemas.py                 # PolicyChunk / RetrievedChunk / QueryResult
├── ingestion/pdf_loader.py    # PDF text extraction + chunking, SSRF-guarded URL fetch
├── retrieval/
│   ├── vector_store.py        # FAISS dense index (persistent + ephemeral)
│   ├── bm25_index.py           # BM25 lexical index
│   ├── hybrid_retriever.py     # Reciprocal Rank Fusion of dense + lexical
│   └── reranker.py             # cross-encoder reranking
└── generation/
    ├── generator.py            # Gemini calls
    ├── prompts.py               # grounded prompt templates
    └── confidence.py            # local confidence scoring

app.py                # Flask API (enterprise + legacy HackRx endpoint)
streamlit_app.py       # chat UI, talks to the pipeline in-process
scripts/build_index.py # rebuild the FAISS index from chunks/all_policy_chunks.json
tests/                 # pytest suite (no network/model downloads required)
```

---

## Setup

```bash
python -m venv venv
```

Windows: `venv\Scripts\activate` · macOS/Linux: `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | yes | Google Gemini API key used for answer generation |
| `HACKRX_AUTH_TOKEN` | only for `/hackrx/run` | Bearer token the legacy endpoint checks; the endpoint returns 503 if unset |
| `GEMINI_MODEL`, `EMBED_MODEL`, `RERANK_MODEL` | no | override the default models |
| `ENABLE_RERANKING`, `ENABLE_HYBRID` | no | toggle pipeline stages, default `true` |

Full list with defaults: [`policy_intel/config.py`](policy_intel/config.py).

---

## Running

**Streamlit chat UI** (recommended for interactive use):

```bash
streamlit run streamlit_app.py
```

**Flask API**:

```bash
python app.py
```

**Rebuild the FAISS index** after changing `chunks/all_policy_chunks.json`:

```bash
python scripts/build_index.py
```

---

## API

### `GET /health`
Returns index size and pipeline status.

### `GET /api/v1/policies`
Lists indexed policy documents and their chunk counts.

### `POST /api/v1/query`
```json
{
  "question": "What is the waiting period for cataract surgery?",
  "documents": "https://example.com/policy.pdf",
  "policies": ["dataset1.pdf"]
}
```
- `question` or `questions` (list) is required.
- `documents` (optional): a public HTTPS/HTTP URL to a PDF, ingested for this
  request only. URLs resolving to loopback, private, or link-local addresses
  (e.g. `127.0.0.1`, `169.254.169.254`, `10.0.0.0/8`) are rejected to prevent SSRF.
- `policies` (optional): restrict the static corpus search to these document names.

Response includes `answer`, `citations` (with source, page, clause, excerpt,
relevance score), `confidence` (score, level, rationale), and `retrieved_count`.

### `POST /hackrx/run`
Legacy single-sentence-answer endpoint, preserved for backward compatibility.
Requires `Authorization: Bearer <HACKRX_AUTH_TOKEN>`; disabled (503) unless
`HACKRX_AUTH_TOKEN` is configured.

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers schemas, confidence scoring, BM25 ranking, the SSRF guard on
PDF ingestion, and API input validation. It does not download embedding models
or call Gemini, so it runs quickly and offline.

---

## Security notes

- PDF URL ingestion validates scheme and resolves the hostname, rejecting
  private/loopback/link-local/reserved IP ranges and disabling redirects, to
  prevent server-side request forgery via `documents`.
- Downloaded PDFs are capped at 50 MB.
- The legacy `/hackrx/run` endpoint requires a constant-time-compared bearer
  token (`HACKRX_AUTH_TOKEN`) and is disabled unless one is configured.
- `.env` is git-ignored; use `.env.example` as the template and never commit
  real API keys.

---

## Deployment

`Dockerfile` builds a slim Python 3.12 image and serves the Flask app with
Gunicorn on the port from `$PORT` (Cloud Run compatible). `Procfile` supports
Heroku-style platforms directly.

---

## Tech Stack

| Category | Technology |
|---|---|
| API | Flask + Gunicorn |
| UI | Streamlit |
| Dense retrieval | FAISS, `sentence-transformers` (MiniLM-L12-v2) |
| Lexical retrieval | `rank-bm25` |
| Reranking | cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| Generation | Google Gemini |
| PDF parsing | `pdfplumber` |

---

## License / Author

**Nethra Krishnan** — B.Tech Computer Science (Data Science), VIT Vellore
GitHub: https://github.com/nethra0906
