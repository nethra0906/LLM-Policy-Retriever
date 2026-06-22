"""
Flask API for the Policy Intelligence Platform.

Preserves the legacy HackRx endpoint while exposing full platform capabilities.
"""

from __future__ import annotations

import os
import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from policy_intel.logging_config import setup_logging
from policy_intel.pipeline import PolicyPipeline

load_dotenv()
logger = setup_logging()

app = Flask(__name__)
_pipeline: PolicyPipeline | None = None


def get_pipeline() -> PolicyPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PolicyPipeline()
    return _pipeline


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
    except Exception as exc:
        logger.exception("Query failed")
        return jsonify({"error": str(exc)}), 500


@app.route("/hackrx/run", methods=["POST"])
def hackrx_run():
    """Legacy HackRx endpoint — returns plain answer strings."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    try:
        data = request.get_json(force=True) or {}
        pdf_url = data.get("documents")
        questions = data.get("questions", [])

        if not questions:
            return jsonify({"error": "No questions provided"}), 400

        pipeline = get_pipeline()
        results = pipeline.query_batch(
            questions=questions,
            pdf_url=pdf_url,
            mode="hackrx",
        )
        answers = [result.answer for result in results]

        return jsonify({"answers": answers})
    except Exception as exc:
        logger.exception("HackRx request failed")
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
