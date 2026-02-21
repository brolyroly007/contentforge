"""Template dataclass models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TemplateField:
    """A single input field for a content template."""

    name: str
    label: str
    type: str = "text"  # text | textarea | select | number
    required: bool = True
    placeholder: str = ""
    default: str = ""
    options: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContentTemplate:
    """A content generation template."""

    id: str
    name: str
    description: str
    category: str  # marketing | social | seo | email | video
    fields: list[TemplateField]
    system_prompt: str
    user_prompt_template: str
    output_format: str = "markdown"  # markdown | structured
    example_output: str = ""
