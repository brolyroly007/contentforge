"""Custom exceptions for ContentForge."""

from __future__ import annotations


class ContentForgeError(Exception):
    """User-facing error with a friendly message."""

    def __init__(self, message: str, hint: str = "") -> None:
        self.message = message
        self.hint = hint
        super().__init__(message)
