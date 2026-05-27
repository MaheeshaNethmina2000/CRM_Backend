from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExtractionResult:
    """
    Unified schema returned by every AI provider.
    All providers MUST map their raw response to this structure.
    The service layer works exclusively with this type — never with
    provider-specific response shapes.
    """

    # Add your domain-specific fields here
    raw_text: str = ""
    confidence_score: float = 0.0
    extracted_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "confidence_score": self.confidence_score,
            "extracted_data": self.extracted_data,
        }


class BaseAIProvider(ABC):
    """
    Strategy interface that every AI provider must implement.

    Contract:
    - Input : file_path (str), content_type (str)
    - Output: ExtractionResult

    Providers are responsible for:
    - Calling their own API / model
    - Parsing the raw response
    - Mapping to ExtractionResult

    Providers are NOT responsible for:
    - Post-processing (done by the service layer)
    - Persistence (done by the service layer)
    - Prompt management (prompts live in app/ai/prompts/)
    """

    @abstractmethod
    def extract(self, file_path: str, content_type: str) -> ExtractionResult:
        """
        Extract structured data from a file.

        Args:
            file_path:    Absolute path to the uploaded file.
            content_type: MIME type (e.g. "image/jpeg", "application/pdf").

        Returns:
            ExtractionResult with all fields populated as best as possible.
        """
        ...
