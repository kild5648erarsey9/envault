"""Lock/unlock secrets to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

LOCK_FILE = ".locks.json"


def _get_lock_path(vault_path: str, env: str) -> Path:
    return Path(vault_path) / env / LOCK_FILE


def _load_locks(vault_path: str, env: str) -> List[str]:
    path = _get_lock_path(vault_path, env)
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save_locks(vault_path: str, env: str, locks: List[str]) -> None:
    path = _get_lock_path(vault_path, env)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(locks, f, indent=2)


def lock_secret(vault_path: str, env: str, key: str) -> List[str]:
    """Lock a secret key so it cannot be modified or deleted."""
    locks = _load_locks(vault_path, env)
    if key not in locks:
        locks.append(key)
        _save_locks(vault_path, env, locks)
    return locks


def unlock_secret(vault_path: str, env: str, key: str) -> List[str]:
    """Unlock a previously locked secret key."""
    locks = _load_locks(vault_path, env)
    if key in locks:
        locks.remove(key)
        _save_locks(vault_path, env, locks)
    return locks


def is_locked(vault_path: str, env: str, key: str) -> bool:
    """Return True if the given key is locked in the given environment."""
    return key in _load_locks(vault_path, env)


def list_locked(vault_path: str, env: str) -> List[str]:
    """Return all locked keys for the given environment."""
    return _load_locks(vault_path, env)


def assert_unlocked(vault_path: str, env: str, key: str) -> None:
    """Raise ValueError if the key is locked."""
    if is_locked(vault_path, env, key):
        raise ValueError(f"Secret '{key}' is locked in environment '{env}'. Unlock it first.")
