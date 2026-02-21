"""Test configuration system."""

from __future__ import annotations

from pathlib import Path

import pytest

from contentforge.config import Config, config_path, load_config, mask_value, save_config, set_value


def test_default_config():
    cfg = Config()
    assert cfg.default_provider == "openai"
    assert cfg.default_temperature == 0.7
    assert cfg.stream is True


def test_load_empty_config():
    cfg = load_config()
    assert cfg.default_provider == "openai"
    assert cfg.openai_api_key == ""


def test_save_and_load(tmp_path: Path):
    cfg = Config()
    cfg.default_provider = "gemini"
    cfg.openai_api_key = "sk-test123"
    save_config(cfg)

    loaded = load_config()
    assert loaded.default_provider == "gemini"
    assert loaded.openai_api_key == "sk-test123"


def test_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CONTENTFORGE_DEFAULT_PROVIDER", "ollama")
    monkeypatch.setenv("CONTENTFORGE_OPENAI_API_KEY", "sk-from-env")

    cfg = load_config()
    assert cfg.default_provider == "ollama"
    assert cfg.openai_api_key == "sk-from-env"
    assert "default_provider" in cfg._env_overrides


def test_set_value():
    cfg = set_value("default_provider", "gemini")
    assert cfg.default_provider == "gemini"

    # Reload to verify persistence
    loaded = load_config()
    assert loaded.default_provider == "gemini"


def test_set_invalid_key():
    with pytest.raises(KeyError, match="Unknown config key"):
        set_value("nonexistent", "value")


def test_mask_value():
    assert mask_value("openai_api_key", "sk-abcdefghijklmnop") == "sk-abcd...mnop"
    assert mask_value("openai_api_key", "short") == "***"
    assert mask_value("default_provider", "openai") == "openai"


def test_config_path_returns_path():
    p = config_path()
    assert p.name == "config.toml"


def test_cast_bool():
    load_config()
    set_value("stream", "false")
    loaded = load_config()
    assert loaded.stream is False


def test_cast_float():
    set_value("default_temperature", "0.5")
    loaded = load_config()
    assert loaded.default_temperature == 0.5
