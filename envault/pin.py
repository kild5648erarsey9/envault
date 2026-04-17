"""Pin a secret to a specific version, preventing accidental overwrites."""

from __future__ import annotations

import json
from pathlib import Path

from envault.vault import get_secret


def _get_pin_path(vault_path: str, env: str) -> Path:
    base = Path(vault_path).parent
    return base / f".pins_{env}.json"


def _load_pins(vault_path: str, env: str) -> dict:
    p = _get_pin_path(vault_path, env)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_path: str, env: str, data: dict) -> None:
    _get_pin_path(vault_path, env).write_text(json.dumps(data, indent=2))


def pin_secret(vault_path: str, env: str, key: str) -> str:
    """Pin key to its current value. Returns the pinned value."""
    value = get_secret(vault_path, env, key)
    if value is None:
        raise KeyError(f"Secret '{key}' not found in env '{env}'")
    pins = _load_pins(vault_path, env)
    pins[key] = value
    _save_pins(vault_path, env, pins)
    return value


def unpin_secret(vault_path: str, env: str, key: str) -> bool:
    """Remove pin for key. Returns True if removed, False if not pinned."""
    pins = _load_pins(vault_path, env)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(vault_path, env, pins)
    return True


def is_pinned(vault_path: str, env: str, key: str) -> bool:
    return key in _load_pins(vault_path, env)


def get_pinned_value(vault_path: str, env: str, key: str) -> str | None:
    return _load_pins(vault_path, env).get(key)


def list_pins(vault_path: str, env: str) -> list[str]:
    return list(_load_pins(vault_path, env).keys())
