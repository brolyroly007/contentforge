"""Test output module."""

from __future__ import annotations

from pathlib import Path

from contentforge import output


def test_save_to_file(tmp_path: Path):
    content = "# Test Content\n\nHello world."
    out_file = tmp_path / "test_output.md"
    result = output.save_to_file(content, str(out_file))
    assert result == out_file
    assert out_file.read_text(encoding="utf-8") == content


def test_save_to_file_creates_dirs(tmp_path: Path):
    out_file = tmp_path / "sub" / "dir" / "output.md"
    output.save_to_file("content", str(out_file))
    assert out_file.exists()


def test_render_markdown(capsys):
    # Should not raise
    output.render_markdown("# Hello\n\nWorld")


def test_render_plain(capsys):
    output.render_plain("Hello world")


def test_render_json(capsys):
    output.render_json("content here", "openai", "gpt-4o-mini", 100)


def test_print_error():
    # Should not raise
    output.print_error("Something went wrong")


def test_copy_to_clipboard_graceful_fail():
    # May or may not work depending on environment, but should not raise
    result = output.copy_to_clipboard("test content")
    assert isinstance(result, bool)
