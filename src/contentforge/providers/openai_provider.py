"""OpenAI provider."""

from __future__ import annotations

import sys
import time
from collections.abc import AsyncIterator
from typing import ClassVar

from contentforge.exceptions import ContentForgeError
from contentforge.providers.base import BaseProvider, GenerationResult


def _handle_openai_error(exc: Exception) -> ContentForgeError:
    """Convert an openai exception to a ContentForgeError."""
    import openai

    if isinstance(exc, openai.AuthenticationError):
        return ContentForgeError(
            "API key inválida o expirada. Verifica con: contentforge config show"
        )
    if isinstance(exc, openai.RateLimitError):
        return ContentForgeError(
            "Rate limit alcanzado. Espera unos minutos e intenta de nuevo."
        )
    if isinstance(exc, openai.APIConnectionError):
        return ContentForgeError(
            "No se pudo conectar a la API de OpenAI. Verifica tu conexión a internet."
        )
    if isinstance(exc, openai.APITimeoutError):
        return ContentForgeError(
            "La solicitud a OpenAI tardó demasiado. Intenta de nuevo."
        )
    if isinstance(exc, openai.APIError):
        return ContentForgeError(f"Error de OpenAI: {exc.message}")
    return ContentForgeError(f"Error inesperado con OpenAI: {exc}")


class OpenAIProvider(BaseProvider):
    name = "openai"
    models: ClassVar[list[str]] = ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o3-mini"]

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> GenerationResult:
        import openai

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        max_retries = 3
        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                break
            except openai.RateLimitError as exc:
                last_exc = exc
                if attempt < max_retries:
                    wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                    print(
                        f"[contentforge] Rate limit alcanzado. "
                        f"Reintentando en {wait}s ({attempt + 1}/{max_retries})...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                raise _handle_openai_error(exc) from exc
            except (
                openai.AuthenticationError,
                openai.APIConnectionError,
                openai.APITimeoutError,
                openai.APIError,
            ) as exc:
                raise _handle_openai_error(exc) from exc
        else:
            # All retries exhausted (shouldn't reach here, but just in case)
            raise _handle_openai_error(last_exc) from last_exc  # type: ignore[arg-type]

        choice = response.choices[0]
        tokens = response.usage.total_tokens if response.usage else 0
        return GenerationResult(
            content=choice.message.content or "",
            provider=self.name,
            model=self.model,
            tokens_used=tokens,
            finish_reason=choice.finish_reason or "stop",
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        import openai

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
        except (
            openai.AuthenticationError,
            openai.RateLimitError,
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.APIError,
        ) as exc:
            raise _handle_openai_error(exc) from exc

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def validate(self) -> None:
        if not self.client.api_key:
            raise ContentForgeError(
                "OpenAI API key no configurada. "
                "Ejecuta: contentforge config set openai_api_key YOUR_KEY"
            )

    def is_available(self) -> bool:
        return bool(self.client.api_key)
