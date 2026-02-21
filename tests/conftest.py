"""Shared test fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect config to a temp dir so tests never touch real config."""
    monkeypatch.setattr("contentforge.config.APP_DIR", tmp_path)
    monkeypatch.setattr("contentforge.config.CONFIG_FILE", tmp_path / "config.toml")
    # Clear any env overrides
    for key in list(os.environ):
        if key.startswith("CONTENTFORGE_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    return tmp_path / "config.toml"
