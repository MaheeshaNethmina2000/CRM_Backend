from app.ai.base_provider import BaseAIProvider


class AIProviderFactory:
    """
    Registry + factory for AI providers.

    Providers register themselves via AIProviderFactory.register().
    The factory creates the correct provider instance from a name string
    (typically read from the AI_PROVIDER env var).

    No if/else chains — adding a new provider never requires touching
    this file or any existing provider.
    """

    _registry: dict[str, type[BaseAIProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[BaseAIProvider]) -> None:
        """Register a provider under a name (e.g. "gemini", "openai")."""
        cls._registry[name.lower()] = provider_class

    @classmethod
    def create(cls, provider_name: str) -> BaseAIProvider:
        """
        Instantiate and return the provider registered under `provider_name`.

        Raises:
            ValueError: if the provider name is not registered.
        """
        key = provider_name.lower()
        if key not in cls._registry:
            available = list(cls._registry.keys())
            raise ValueError(
                f"Unknown AI provider: '{provider_name}'. "
                f"Available providers: {available}"
            )
        return cls._registry[key]()

    @classmethod
    def available_providers(cls) -> list[str]:
        """Return the list of currently registered provider names."""
        return list(cls._registry.keys())
