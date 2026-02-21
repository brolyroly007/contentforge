"""Test CLI entry points."""

from __future__ import annotations

from typer.testing import CliRunner

from contentforge import __version__
from contentforge.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output.lower()
    assert "templates" in result.output.lower()
    assert "providers" in result.output.lower()
    assert "config" in result.output.lower()


def test_generate_help():
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "blog" in result.output
    assert "social" in result.output
    assert "email" in result.output


def test_templates_list():
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "blog" in result.output.lower()


def test_templates_show():
    result = runner.invoke(app, ["templates", "show", "blog"])
    assert result.exit_code == 0
    assert "topic" in result.output.lower()


def test_templates_show_unknown():
    result = runner.invoke(app, ["templates", "show", "nonexistent"])
    assert result.exit_code == 1


def test_config_show():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "default_provider" in result.output


def test_config_path():
    result = runner.invoke(app, ["config", "path"])
    assert result.exit_code == 0
    # Path may wrap across lines on Windows, so join and check
    assert "config.toml" in result.output.replace("\n", "")


def test_config_set_and_persist():
    result = runner.invoke(app, ["config", "set", "default_provider", "gemini"])
    assert result.exit_code == 0
    assert "gemini" in result.output

    # Verify it persisted
    result = runner.invoke(app, ["config"])
    assert "gemini" in result.output


def test_config_set_invalid_key():
    result = runner.invoke(app, ["config", "set", "nonexistent_key", "value"])
    assert result.exit_code == 1
