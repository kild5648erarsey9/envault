"""Secret inheritance: allow an environment to inherit secrets from a parent env."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.vault import get_secret, list_keys


def _get_inherit_path(vault_path: str) -> Path:
    return Path(vault_path) / "_inherit.json"


def _load_inherit(vault_path: str) -> dict:
    p = _get_inherit_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_inherit(vault_path: str, data: dict) -> None:
    p = _get_inherit_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def set_parent(vault_path: str, env: str, parent: str) -> str:
    """Set *parent* as the inheritance source for *env*."""
    if env == parent:
        raise ValueError("An environment cannot inherit from itself.")
    data = _load_inherit(vault_path)
    data[env] = parent
    _save_inherit(vault_path, data)
    return parent


def get_parent(vault_path: str, env: str) -> Optional[str]:
    """Return the parent env for *env*, or None if not set."""
    return _load_inherit(vault_path).get(env)


def remove_parent(vault_path: str, env: str) -> None:
    """Remove the inheritance link for *env*."""
    data = _load_inherit(vault_path)
    data.pop(env, None)
    _save_inherit(vault_path, data)


def resolve_secret(
    vault_path: str, env: str, key: str, password: str
) -> Optional[str]:
    """Return the secret for *key* in *env*, falling back to parent envs.

    Raises RuntimeError if a cycle is detected.
    """
    visited: set[str] = set()
    current = env
    while current is not None:
        if current in visited:
            raise RuntimeError(
                f"Inheritance cycle detected involving environment '{current}'."
            )
        visited.add(current)
        value = get_secret(vault_path, current, key, password)
        if value is not None:
            return value
        current = get_parent(vault_path, current)
    return None


def list_resolved_keys(vault_path: str, env: str, password: str) -> list[str]:
    """Return all keys visible from *env*, including those inherited."""
    visited: set[str] = set()
    all_keys: set[str] = set()
    current: Optional[str] = env
    while current is not None:
        if current in visited:
            break
        visited.add(current)
        all_keys.update(list_keys(vault_path, current, password))
        current = get_parent(vault_path, current)
    return sorted(all_keys)
