"""Alias management: map short names to secret keys."""
from __future__ import annotations
import json
from pathlib import Path


def _get_alias_path(vault_path: str) -> Path:
    return Path(vault_path).parent / "aliases.json"


def _load_aliases(vault_path: str) -> dict:
    p = _get_alias_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(vault_path: str, data: dict) -> None:
    _get_alias_path(vault_path).write_text(json.dumps(data, indent=2))


def set_alias(vault_path: str, alias: str, key: str, env: str) -> dict:
    alias = alias.strip()
    if not alias:
        raise ValueError("Alias must not be empty.")
    data = _load_aliases(vault_path)
    data[alias] = {"key": key, "env": env}
    _save_aliases(vault_path, data)
    return data[alias]


def get_alias(vault_path: str, alias: str) -> dict | None:
    return _load_aliases(vault_path).get(alias)


def remove_alias(vault_path: str, alias: str) -> bool:
    data = _load_aliases(vault_path)
    if alias not in data:
        return False
    del data[alias]
    _save_aliases(vault_path, data)
    return True


def list_aliases(vault_path: str) -> dict:
    return _load_aliases(vault_path)


def resolve_alias(vault_path: str, alias: str) -> tuple[str, str] | None:
    """Return (key, env) tuple or None if alias not found."""
    entry = get_alias(vault_path, alias)
    if entry is None:
        return None
    return entry["key"], entry["env"]
