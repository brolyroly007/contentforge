"""Provider factory for ContentForge."""

from __future__ import annotations

from contentforge.config import load_config
from contentforge.providers.base import BaseProvider, GenerationResult

__all__ = ["BaseProvider", "GenerationResult", "get_provider", "list_providers"]


def get_provider(name: str | None = None, model: str | None = None) -> BaseProvider:
    """Create and return a provider instance.

    Uses a factory-per-call pattern (CLI is short-lived, no singleton needed).
    """
    cfg = load_config()
    name = name or cfg.default_provider

    if name == "openai":
        from contentforge.providers.openai_provider import OpenAIProvider

        if not cfg.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Run: contentforge config set openai_api_key YOUR_KEY"
            )
        return OpenAIProvider(api_key=cfg.openai_api_key, model=model or cfg.openai_model)

    if name == "gemini":
        from contentforge.providers.gemini_provider import GeminiProvider

        if not cfg.gemini_api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Run: contentforge config set gemini_api_key YOUR_KEY"
            )
        return GeminiProvider(api_key=cfg.gemini_api_key, model=model or cfg.gemini_model)

    if name == "ollama":
        from contentforge.providers.ollama_provider import OllamaProvider

        return OllamaProvider(base_url=cfg.ollama_base_url, model=model or cfg.ollama_model)

    raise ValueError(f"Unknown provider: {name!r}. Available: openai, gemini, ollama")


def list_providers() -> list[dict]:
    """Return metadata for all known providers."""
    cfg = load_config()
    providers = []

    # OpenAI
    from contentforge.providers.openai_provider import OpenAIProvider

    if cfg.openai_api_key:
        p = OpenAIProvider(api_key=cfg.openai_api_key, model=cfg.openai_model)
    else:
        p = type("_Stub", (), {"name": "openai", "models": OpenAIProvider.models, "is_available": lambda self: False})()  # type: ignore[assignment]
    providers.append({"name": "openai", "models": OpenAIProvider.models, "available": p.is_available(), "default_model": cfg.openai_model})

    # Gemini
    from contentforge.providers.gemini_provider import GeminiProvider

    if cfg.gemini_api_key:
        p = GeminiProvider(api_key=cfg.gemini_api_key, model=cfg.gemini_model)
    else:
        p = type("_Stub", (), {"name": "gemini", "models": GeminiProvider.models, "is_available": lambda self: False})()  # type: ignore[assignment]
    providers.append({"name": "gemini", "models": GeminiProvider.models, "available": p.is_available(), "default_model": cfg.gemini_model})

    # Ollama
    from contentforge.providers.ollama_provider import OllamaProvider

    op = OllamaProvider(base_url=cfg.ollama_base_url, model=cfg.ollama_model)
    providers.append({"name": "ollama", "models": OllamaProvider.models, "available": op.is_available(), "default_model": cfg.ollama_model})

    return providers
