"""Ollama (local) provider."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import ClassVar

import httpx

from contentforge.exceptions import ContentForgeError
from contentforge.providers.base import BaseProvider, GenerationResult


class OllamaProvider(BaseProvider):
    name = "ollama"
    models: ClassVar[list[str]] = ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "gemma2"]

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> GenerationResult:
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.ConnectError as exc:
            raise ContentForgeError(
                "No se pudo conectar a Ollama. ¿Está corriendo? Ejecuta: ollama serve"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ContentForgeError(
                "Ollama tardó demasiado en responder. Verifica que el modelo esté descargado."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ContentForgeError(
                "Respuesta inválida de Ollama. ¿Está corriendo correctamente?"
            ) from exc

        tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
        return GenerationResult(
            content=data.get("response", ""),
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
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client, client.stream(
                "POST", f"{self.base_url}/api/generate", json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    if data.get("done"):
                        break
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
        except httpx.ConnectError as exc:
            raise ContentForgeError(
                "No se pudo conectar a Ollama. ¿Está corriendo? Ejecuta: ollama serve"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ContentForgeError(
                "Ollama tardó demasiado en responder. Verifica que el modelo esté descargado."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ContentForgeError(
                "Respuesta inválida de Ollama. ¿Está corriendo correctamente?"
            ) from exc

    def validate(self) -> None:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            resp.raise_for_status()
        except httpx.ConnectError:
            raise ContentForgeError(
                "No se pudo conectar a Ollama. ¿Está corriendo? Ejecuta: ollama serve"
            ) from None
        except httpx.TimeoutException:
            raise ContentForgeError(
                "Ollama no respondió a tiempo. Verifica que esté corriendo correctamente."
            ) from None
        except httpx.HTTPStatusError:
            raise ContentForgeError(
                "Ollama respondió con un error. Verifica que esté corriendo correctamente."
            ) from None

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False
