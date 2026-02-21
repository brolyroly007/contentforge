"""Test provider system."""

from __future__ import annotations

from typing import ClassVar

import pytest

from contentforge.providers.base import BaseProvider, GenerationResult


def test_generation_result():
    r = GenerationResult(content="hello", provider="test", model="test-1")
    assert r.content == "hello"
    assert r.tokens_used == 0
    assert r.finish_reason == "stop"


def test_base_provider_info():
    """Test that a concrete subclass returns proper info."""

    class FakeProvider(BaseProvider):
        name = "fake"
        models: ClassVar[list[str]] = ["fake-1"]

        async def generate(self, prompt, system_prompt="", temperature=0.7, max_tokens=2000):
            return GenerationResult(content="", provider="fake", model="fake-1")

        async def stream(self, prompt, system_prompt="", temperature=0.7, max_tokens=2000):
            yield "chunk"

        def is_available(self):
            return True

    p = FakeProvider()
    info = p.info()
    assert info["name"] == "fake"
    assert info["available"] is True
    assert "fake-1" in info["models"]


def test_openai_provider_attributes():
    from contentforge.providers.openai_provider import OpenAIProvider

    assert OpenAIProvider.name == "openai"
    assert "gpt-4o-mini" in OpenAIProvider.models


def test_gemini_provider_attributes():
    from contentforge.providers.gemini_provider import GeminiProvider

    assert GeminiProvider.name == "gemini"
    assert "gemini-2.0-flash" in GeminiProvider.models


def test_ollama_provider_attributes():
    from contentforge.providers.ollama_provider import OllamaProvider

    assert OllamaProvider.name == "ollama"
    assert "llama3.2" in OllamaProvider.models


def test_ollama_provider_init():
    from contentforge.providers.ollama_provider import OllamaProvider

    p = OllamaProvider(base_url="http://localhost:11434/", model="mistral")
    assert p.base_url == "http://localhost:11434"
    assert p.model == "mistral"


def test_get_provider_unknown():
    from contentforge.providers import get_provider

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent")


def test_get_provider_openai_no_key():
    from contentforge.providers import get_provider

    with pytest.raises(ValueError, match="API key not configured"):
        get_provider("openai")


def test_get_provider_gemini_no_key():
    from contentforge.providers import get_provider

    with pytest.raises(ValueError, match="API key not configured"):
        get_provider("gemini")


def test_get_provider_ollama():
    from contentforge.providers import get_provider

    p = get_provider("ollama")
    assert p.name == "ollama"


def test_list_providers():
    from contentforge.providers import list_providers

    providers = list_providers()
    names = [p["name"] for p in providers]
    assert "openai" in names
    assert "gemini" in names
    assert "ollama" in names
