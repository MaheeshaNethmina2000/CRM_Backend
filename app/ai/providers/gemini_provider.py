import base64
import json
from pathlib import Path

import requests

from app.ai.base_provider import BaseAIProvider, ExtractionResult
from app.ai.prompts.sample_prompt import SAMPLE_EXTRACTION_PROMPT
from app.config.config import AI_API_URL, AI_MODEL, AI_REQUEST_TIMEOUT, GEMINI_API_KEY
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini provider (REST API, vision-capable models).

    Relevant env vars:
        AI_PROVIDER=gemini
        AI_MODEL=gemini-2.5-flash          (or any vision-capable Gemini model)
        GEMINI_API_KEY=<your key>
        AI_API_URL=https://generativelanguage.googleapis.com/v1beta/models
        AI_REQUEST_TIMEOUT=180
    """

    def extract(self, file_path: str, content_type: str) -> ExtractionResult:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")

        raw_dict = self._call_api(file_path, content_type)
        return self._map_to_result(raw_dict)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_api(self, file_path: str, content_type: str) -> dict:
        encoded_file = base64.b64encode(Path(file_path).read_bytes()).decode("utf-8")
        request_url = f"{AI_API_URL}/{AI_MODEL}:generateContent"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SAMPLE_EXTRACTION_PROMPT},
                        {"text": "Extract structured data from this file."},
                        {
                            "inline_data": {
                                "mime_type": content_type,
                                "data": encoded_file,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0,
            },
        }

        logger.debug(
            f"[GeminiProvider] Calling API. url={request_url}, model={AI_MODEL}, "
            f"mime_type={content_type}, encoded_size={len(encoded_file)}"
        )

        response = requests.post(
            request_url,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=AI_REQUEST_TIMEOUT,
        )

        logger.debug(f"[GeminiProvider] Response status={response.status_code}")

        if not response.ok:
            logger.error(
                f"[GeminiProvider] Request failed. status={response.status_code}, "
                f"body={response.text[:1000]}"
            )
            response.raise_for_status()

        response_json = response.json()
        output_text = self._extract_output_text(response_json)

        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            sanitized = self._sanitize_json_string(output_text)
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError as exc:
                raise ValueError("Gemini response was not valid JSON") from exc

    def _map_to_result(self, raw: dict) -> ExtractionResult:
        """Map the raw Gemini JSON dict to the provider-agnostic ExtractionResult."""
        return ExtractionResult(
            raw_text=raw.get("raw_text") or "",
            confidence_score=float(raw.get("confidence_score") or 0.0),
            extracted_data=raw,
        )

    # ------------------------------------------------------------------
    # JSON parsing utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_output_text(response_json: dict) -> str:
        for candidate in response_json.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    return part["text"]
        return "{}"

    @staticmethod
    def _str_or_none(value) -> str | None:
        return str(value) if value is not None else None

    @staticmethod
    def _sanitize_json_string(value: str) -> str:
        trimmed = value.strip()
        start = trimmed.find("{")
        end = trimmed.rfind("}")
        if start != -1 and end != -1 and end > start:
            trimmed = trimmed[start:end + 1]

        chars = []
        in_string = False
        escaped = False

        for char in trimmed:
            if in_string:
                if escaped:
                    chars.append(char)
                    escaped = False
                    continue
                if char == "\\":
                    chars.append(char)
                    escaped = True
                    continue
                if char == "\"":
                    chars.append(char)
                    in_string = False
                    continue
                if ord(char) < 32:
                    escape_map = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}
                    chars.append(escape_map.get(char, f"\\u{ord(char):04x}"))
                    continue
                chars.append(char)
                continue

            chars.append(char)
            if char == "\"":
                in_string = True

        return "".join(chars)
