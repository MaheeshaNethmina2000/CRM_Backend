"""
OpenAI provider (GPT-4o Vision).

To activate:
  1. pip install openai
  2. Set env vars:
       AI_PROVIDER=openai
       OPENAI_API_KEY=<your key>
       AI_MODEL=gpt-4o          (or gpt-4o-mini)
  3. Uncomment the two lines in app/ai/providers/__init__.py

Nothing else changes in the rest of the codebase.
"""

import base64
import json
from pathlib import Path

from app.ai.base_provider import BaseAIProvider, ExtractionResult
from app.ai.prompts.sample_prompt import SAMPLE_EXTRACTION_PROMPT
from app.config.config import AI_MODEL, AI_REQUEST_TIMEOUT
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)

# Lazily imported so the app doesn't crash when openai is not installed
# and AI_PROVIDER != "openai".
try:
    from openai import OpenAI  # type: ignore[import]
except ImportError:
    OpenAI = None  # type: ignore[assignment, misc]


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI GPT-4o (vision) provider.

    Relevant env vars:
        AI_PROVIDER=openai
        AI_MODEL=gpt-4o
        OPENAI_API_KEY=<your key>
        AI_REQUEST_TIMEOUT=180
    """

    def extract(self, file_path: str, content_type: str) -> ExtractionResult:
        if OpenAI is None:
            raise RuntimeError(
                "openai package is not installed. Run: pip install openai"
            )

        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")

        client = OpenAI(api_key=api_key, timeout=AI_REQUEST_TIMEOUT)

        encoded = base64.b64encode(Path(file_path).read_bytes()).decode("utf-8")
        data_url = f"data:{content_type};base64,{encoded}"

        logger.debug(f"[OpenAIProvider] Calling API. model={AI_MODEL}")

        response = client.chat.completions.create(
            model=AI_MODEL,
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SAMPLE_EXTRACTION_PROMPT},
                        {"type": "text", "text": "Extract structured data from this file."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )

        raw_text = response.choices[0].message.content or "{}"
        raw = json.loads(raw_text)
        return self._map_to_result(raw)

    def _map_to_result(self, raw: dict) -> ExtractionResult:
        return ExtractionResult(
            raw_text=raw.get("raw_text") or "",
            confidence_score=float(raw.get("confidence_score") or 0.0),
            extracted_data=raw,
        )

    @staticmethod
    def _str_or_none(value) -> str | None:
        return str(value) if value is not None else None
