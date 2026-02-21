"""Test template system."""

from __future__ import annotations

import pytest

from contentforge.templates import get_template, list_templates
from contentforge.templates.models import ContentTemplate, TemplateField
from contentforge.templates.registry import TEMPLATES


def test_all_templates_registered():
    assert len(TEMPLATES) == 8


def test_list_templates():
    templates = list_templates()
    assert len(templates) == 8
    assert all(isinstance(t, ContentTemplate) for t in templates)


def test_template_ids():
    expected = {"blog", "social", "email", "tweet-thread", "ad", "seo", "product", "youtube"}
    assert set(TEMPLATES.keys()) == expected


def test_get_template():
    t = get_template("blog")
    assert t.id == "blog"
    assert t.name == "Blog Post"
    assert t.category == "marketing"


def test_get_template_unknown():
    with pytest.raises(KeyError, match="Unknown template"):
        get_template("nonexistent")


def test_blog_template_fields():
    t = get_template("blog")
    field_names = [f.name for f in t.fields]
    assert "topic" in field_names
    assert "tone" in field_names


def test_template_has_prompts():
    for t in list_templates():
        assert t.system_prompt, f"{t.id} missing system_prompt"
        assert t.user_prompt_template, f"{t.id} missing user_prompt_template"


def test_template_fields_have_names():
    for t in list_templates():
        for f in t.fields:
            assert f.name, f"Field in {t.id} missing name"
            assert f.label, f"Field {f.name} in {t.id} missing label"


def test_select_fields_have_options():
    for t in list_templates():
        for f in t.fields:
            if f.type == "select":
                assert f.options, f"Select field {f.name} in {t.id} has no options"


def test_template_field_dataclass():
    f = TemplateField(name="test", label="Test")
    assert f.required is True
    assert f.type == "text"
    assert f.options == []


def test_content_template_dataclass():
    t = ContentTemplate(
        id="test",
        name="Test",
        description="A test template",
        category="test",
        fields=[],
        system_prompt="system",
        user_prompt_template="user {var}",
    )
    assert t.output_format == "markdown"
