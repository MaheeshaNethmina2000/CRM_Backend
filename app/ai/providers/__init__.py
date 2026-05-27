# Auto-register all providers when this package is imported.
# To add a new provider: create the file, register it here — nothing else changes.

from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.provider_factory import AIProviderFactory

AIProviderFactory.register("mock", MockProvider)
AIProviderFactory.register("gemini", GeminiProvider)

# Future providers — uncomment when ready:
# from app.ai.providers.openai_provider import OpenAIProvider
# from app.ai.providers.anthropic_provider import AnthropicProvider
# AIProviderFactory.register("openai", OpenAIProvider)
# AIProviderFactory.register("anthropic", AnthropicProvider)
