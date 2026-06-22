"""Gemini answer generation."""

from __future__ import annotations

import google.generativeai as genai

from policy_intel.config import GEMINI_API_KEY, GEMINI_MODEL
from policy_intel.generation.prompts import hackrx_prompt, platform_prompt
from policy_intel.logging_config import setup_logging
from policy_intel.schemas import RetrievedChunk

logger = setup_logging()


class AnswerGenerator:
    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in the environment")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def generate_hackrx(self, query: str, chunks: list[RetrievedChunk]) -> str:
        prompt = hackrx_prompt(query, chunks)
        logger.debug("HackRx prompt length: %d chars", len(prompt))
        response = self.model.generate_content(prompt)
        return (response.text or "").strip()

    def generate_platform(self, query: str, chunks: list[RetrievedChunk]) -> str:
        prompt = platform_prompt(query, chunks)
        logger.debug("Platform prompt length: %d chars", len(prompt))
        response = self.model.generate_content(prompt)
        return (response.text or "").strip()
