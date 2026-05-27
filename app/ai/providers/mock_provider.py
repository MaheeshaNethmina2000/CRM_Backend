from pathlib import Path

from app.ai.base_provider import BaseAIProvider, ExtractionResult


class MockProvider(BaseAIProvider):
    """
    Deterministic mock provider for local development and testing.
    Returns a predictable result based on the filename — no API calls made.
    """

    def extract(self, file_path: str, content_type: str) -> ExtractionResult:
        file_name = Path(file_path).name
        raw = f"Mock OCR result for {file_name}"

        return ExtractionResult(
            raw_text=raw,
            confidence_score=0.99,
            extracted_data={"mock": True, "file": file_name},
        )
