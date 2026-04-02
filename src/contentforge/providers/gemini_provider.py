"""Google Gemini provider."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import ClassVar

from contentforge.exceptions import ContentForgeError
from contentforge.providers.base import BaseProvider, GenerationResult


def _handle_gemini_error(exc: Exception) -> ContentForgeError:
    """Convert a Gemini exception to a ContentForgeError."""
    try:
        from google.api_core.exceptions import PermissionDenied, ResourceExhausted
    except ImportError:
        return ContentForgeError(f"Error inesperado con Gemini: {exc}")

    if isinstance(exc, PermissionDenied):
        return ContentForgeError(
            "API key inválida o expirada. Verifica con: contentforge config show"
        )
    if isinstance(exc, ResourceExhausted):
        return ContentForgeError(
            "Rate limit alcanzado. Espera unos minutos e intenta de nuevo."
        )
    return ContentForgeError(f"Error de Gemini: {exc}")


_BLOCKED_REASONS = {"SAFETY", "RECITATION", "OTHER", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"}

_BLOCKED_MSG = (
    "La respuesta fue bloqueada por el filtro de seguridad de Gemini. "
    "Intenta reformular tu solicitud."
)


def _check_blocked_response(response) -> None:
    """Raise ContentForgeError if the Gemini response was blocked."""
    if not response.candidates:
        raise ContentForgeError(_BLOCKED_MSG)

    finish_reason = getattr(response.candidates[0], "finish_reason", None)
    if finish_reason is not None:
        reason_name = finish_reason.name if hasattr(finish_reason, "name") else str(finish_reason)
        if reason_name in _BLOCKED_REASONS:
            raise ContentForgeError(_BLOCKED_MSG)


class GeminiProvider(BaseProvider):
    name = "gemini"
    models: ClassVar[list[str]] = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._genai = genai
        self._api_key = api_key
        self.model = model

    def _get_model(self, system_prompt: str = ""):
        kwargs = {"model_name": self.model}
        if system_prompt:
            kwargs["system_instruction"] = system_prompt
        return self._genai.GenerativeModel(**kwargs)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> GenerationResult:
        model = self._get_model(system_prompt)
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config=self._genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
        except Exception as exc:
            raise _handle_gemini_error(exc) from exc

        # Check if response was blocked by safety filters
        _check_blocked_response(response)

        tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            tokens = getattr(response.usage_metadata, "total_token_count", 0)
        return GenerationResult(
            content=response.text,
            provider=self.name,
            model=self.model,
            tokens_used=tokens,
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        model = self._get_model(system_prompt)
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config=self._genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                stream=True,
            )
        except Exception as exc:
            raise _handle_gemini_error(exc) from exc

        async for chunk in response:
            try:
                if chunk.text:
                    yield chunk.text
            except (AttributeError, ValueError):
                continue

    def validate(self) -> None:
        if not self._api_key:
            raise ContentForgeError(
                "Gemini API key no configurada. "
                "Ejecuta: contentforge config set gemini_api_key YOUR_KEY"
            )

    def is_available(self) -> bool:
        return bool(self._api_key)
