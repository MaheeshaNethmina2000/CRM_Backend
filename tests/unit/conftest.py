"""
Unit-level fixtures — mock all external dependencies so tests run
with zero network calls, zero DB hits, and zero side effects.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture()
def mock_db():
    """A MagicMock standing in for a SQLAlchemy session."""
    return MagicMock()


@pytest.fixture()
def mock_ai_provider():
    """Mock AI provider — prevents real API calls during unit tests."""
    from app.ai.base_provider import ExtractionResult
    provider = MagicMock()
    provider.extract.return_value = ExtractionResult(
        raw_text="mocked result",
        confidence_score=0.99,
        extracted_data={"mock": True},
    )
    return provider


@pytest.fixture()
def mock_email_service():
    """Mock email service — prevents real emails being sent during unit tests."""
    service = MagicMock()
    service.send.return_value = True
    return service
