"""Template system for ContentForge."""

from __future__ import annotations

from contentforge.templates.models import ContentTemplate, TemplateField
from contentforge.templates.registry import TEMPLATES

__all__ = ["ContentTemplate", "TemplateField", "get_template", "list_templates"]


def get_template(template_id: str) -> ContentTemplate:
    """Get a template by ID or raise KeyError."""
    if template_id not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES))
        raise KeyError(f"Unknown template: {template_id!r}. Available: {available}")
    return TEMPLATES[template_id]


def list_templates() -> list[ContentTemplate]:
    """Return all registered templates."""
    return list(TEMPLATES.values())
