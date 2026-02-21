"""Google Gemini provider."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import ClassVar

from contentforge.providers.base import BaseProvider, GenerationResult


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
        response = await model.generate_content_async(
            prompt,
            generation_config=self._genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
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
        response = await model.generate_content_async(
            prompt,
            generation_config=self._genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
            stream=True,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    def is_available(self) -> bool:
        return bool(self._api_key)
