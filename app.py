"""
Flask API for the Policy Intelligence Platform.

Preserves the legacy HackRx endpoint while exposing full platform capabilities.
"""

from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from policy_intel.ingestion.pdf_loader import UnsafePdfUrlError
from policy_intel.logging_config import setup_logging
from policy_intel.pipeline import PolicyPipeline

load_dotenv()
logger = setup_logging()

app = Flask(__name__)
_pipeline: PolicyPipeline | None = None
HACKRX_AUTH_TOKEN = os.environ.get("HACKRX_AUTH_TOKEN")


def get_pipeline() -> PolicyPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PolicyPipeline()
    return _pipeline


MAX_QUESTIONS_PER_REQUEST = 20
MAX_QUESTION_LENGTH = 2000


def _validate_query_inputs(questions, pdf_url, policy_filter) -> str | None:
    """Return an error message if the request body is malformed, else None."""
    if not isinstance(questions, list) or not questions:
        return "'questions' must be a non-empty list of strings"
    if len(questions) > MAX_QUESTIONS_PER_REQUEST:
        return f"Too many questions; max {MAX_QUESTIONS_PER_REQUEST} per request"
    for q in questions:
        if not isinstance(q, str) or not q.strip():
            return "Each question must be a non-empty string"
        if len(q) > MAX_QUESTION_LENGTH:
            return f"Question exceeds max length of {MAX_QUESTION_LENGTH} characters"

    if pdf_url is not None and not isinstance(pdf_url, str):
        return "'documents' must be a URL string"

    if policy_filter is not None and (
        not isinstance(policy_filter, list) or not all(isinstance(p, str) for p in policy_filter)
    ):
        return "'policies' must be a list of strings"

    return None


@app.route("/health", methods=["GET"])
def health():
    try:
        pipeline = get_pipeline()
        return jsonify(
            {
                "status": "ok",
                "chunks_indexed": len(pipeline.vector_store.chunks),
                "policies": len(pipeline.list_policies()),
            }
        )
    except Exception as exc:
        return jsonify({"status": "error", "detail": str(exc)}), 503


@app.route("/api/v1/policies", methods=["GET"])
def list_policies():
    try:
        policies = get_pipeline().list_policies()
        return jsonify({"policies": policies})
    except Exception as exc:
        logger.exception("Failed to list policies")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/v1/query", methods=["POST"])
def query():
    """
    Enterprise query endpoint with citations and confidence.

    Body:
      - question (str) OR questions (list[str])
      - documents (str, optional): PDF URL for dynamic ingestion
      - policies (list[str], optional): filter by source_doc names
    """
    try:
        data = request.get_json(force=True) or {}
        pdf_url = data.get("documents")
        policy_filter = data.get("policies")

        if "questions" in data:
            questions = data["questions"]
        elif "question" in data:
            questions = [data["question"]]
        else:
            return jsonify({"error": "Provide 'question' or 'questions'"}), 400

        error = _validate_query_inputs(questions, pdf_url, policy_filter)
        if error:
            return jsonify({"error": error}), 400

        pipeline = get_pipeline()
        results = pipeline.query_batch(
            questions=questions,
            pdf_url=pdf_url,
            policy_filter=policy_filter,
            mode="platform",
        )

        payload = {
            "results": [result.to_dict() for result in results],
        }
        if len(results) == 1:
            payload["result"] = results[0].to_dict()

        return jsonify(payload)
    except UnsafePdfUrlError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception("Query failed")
        return jsonify({"error": str(exc)}), 500


@app.route("/hackrx/run", methods=["POST"])
def hackrx_run():
    """Legacy HackRx endpoint — returns plain answer strings."""
    if not HACKRX_AUTH_TOKEN:
        logger.error("HACKRX_AUTH_TOKEN is not configured; refusing request.")
        return jsonify({"error": "Endpoint is not configured"}), 503

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else ""
    if not token or not secrets.compare_digest(token, HACKRX_AUTH_TOKEN):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    try:
        data = request.get_json(force=True) or {}
        pdf_url = data.get("documents")
        questions = data.get("questions", [])

        error = _validate_query_inputs(questions, pdf_url, None)
        if error:
            return jsonify({"error": error}), 400

        pipeline = get_pipeline()
        results = pipeline.query_batch(
            questions=questions,
            pdf_url=pdf_url,
            mode="hackrx",
        )
        answers = [result.answer for result in results]

        return jsonify({"answers": answers})
    except UnsafePdfUrlError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception("HackRx request failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
