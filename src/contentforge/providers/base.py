"""Base provider interface and result dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result of a content generation call."""

    content: str
    provider: str
    model: str
    tokens_used: int = 0
    finish_reason: str = "stop"


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str
    models: list[str]

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> GenerationResult:
        """Generate content (non-streaming)."""

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Yield content chunks for streaming."""
        yield ""  # pragma: no cover

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured / reachable."""

    def info(self) -> dict:
        """Provider metadata."""
        return {
            "name": self.name,
            "models": self.models,
            "available": self.is_available(),
        }
