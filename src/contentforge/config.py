"""TOML configuration with environment variable overrides."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, fields
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib  # type: ignore[no-redef]

import tomli_w

APP_DIR = Path.home() / ".contentforge"
CONFIG_FILE = APP_DIR / "config.toml"

# Keys that should be masked when displayed
_SENSITIVE_KEYS = {"openai_api_key", "gemini_api_key"}

# Environment variable prefix
_ENV_PREFIX = "CONTENTFORGE_"


@dataclass
class Config:
    """Application configuration loaded from TOML + env vars."""

    # Provider keys
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Default models
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-2.0-flash"
    ollama_model: str = "llama3.2"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Defaults
    default_provider: str = "openai"
    default_format: str = "markdown"
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    stream: bool = True

    # Internal: tracks which fields came from env so we don't persist them
    _env_overrides: set = field(default_factory=set, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_env_overrides", set())


def config_path() -> Path:
    """Return the path to the config file."""
    return CONFIG_FILE


def _ensure_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load config from TOML file, then override with env vars."""
    cfg = Config()

    # Load from TOML
    if CONFIG_FILE.exists():
        raw = CONFIG_FILE.read_bytes()
        data = tomllib.loads(raw.decode())
        for f in fields(cfg):
            if f.name.startswith("_"):
                continue
            if f.name in data:
                object.__setattr__(cfg, f.name, f.type and _cast(data[f.name], f.type))

    # Override with env vars  (CONTENTFORGE_OPENAI_API_KEY etc.)
    for f in fields(cfg):
        if f.name.startswith("_"):
            continue
        env_key = _ENV_PREFIX + f.name.upper()
        env_val = os.environ.get(env_key)
        if env_val is not None:
            object.__setattr__(cfg, f.name, _cast(env_val, f.type))
            cfg._env_overrides.add(f.name)

    return cfg


def save_config(cfg: Config) -> None:
    """Persist config to TOML (skips env-override fields)."""
    _ensure_dir()
    data: dict = {}
    for f in fields(cfg):
        if f.name.startswith("_"):
            continue
        val = getattr(cfg, f.name)
        # Only write non-default or explicitly-set values
        default_val = getattr(Config(), f.name)
        if val != default_val:
            data[f.name] = val
    CONFIG_FILE.write_bytes(tomli_w.dumps(data).encode())


def set_value(key: str, value: str) -> Config:
    """Set a single config key and persist."""
    cfg = load_config()
    valid_keys = {f.name for f in fields(cfg) if not f.name.startswith("_")}
    if key not in valid_keys:
        raise KeyError(f"Unknown config key: {key!r}. Valid keys: {', '.join(sorted(valid_keys))}")
    target_field = next(f for f in fields(cfg) if f.name == key)
    object.__setattr__(cfg, key, _cast(value, target_field.type))
    save_config(cfg)
    return cfg


def mask_value(key: str, value: str) -> str:
    """Mask sensitive values for display."""
    if key in _SENSITIVE_KEYS and value:
        return value[:7] + "..." + value[-4:] if len(value) > 14 else "***"
    return value


def _cast(value: object, type_hint: str) -> object:
    """Cast a raw value to the correct Python type."""
    if type_hint == "float":
        return float(value)  # type: ignore[arg-type]
    if type_hint == "int":
        return int(value)  # type: ignore[arg-type]
    if type_hint == "bool":
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")
    return str(value)
