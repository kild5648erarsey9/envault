"""Secret rotation utilities for envault."""

from datetime import datetime, timezone
from typing import Optional

from envault.vault import get_secret, set_secret, list_keys, _load_raw, _save_raw


ROTATION_META_KEY = "__rotation_meta__"


def _get_meta(vault_path: str, env: str) -> dict:
    """Load rotation metadata for an environment."""
    raw = _load_raw(vault_path)
    return raw.get(env, {}).get(ROTATION_META_KEY, {})


def _set_meta(vault_path: str, env: str, meta: dict) -> None:
    """Persist rotation metadata for an environment."""
    raw = _load_raw(vault_path)
    if env not in raw:
        raw[env] = {}
    raw[env][ROTATION_META_KEY] = meta
    _save_raw(vault_path, raw)


def record_rotation(vault_path: str, env: str, key: str) -> str:
    """Record the current UTC timestamp as the last rotation time for a key.

    Returns the ISO-formatted timestamp string.
    """
    now = datetime.now(timezone.utc).isoformat()
    meta = _get_meta(vault_path, env)
    meta[key] = {"last_rotated": now}
    _set_meta(vault_path, env, meta)
    return now


def get_rotation_info(vault_path: str, env: str, key: str) -> Optional[dict]:
    """Return rotation metadata for a specific key, or None if not recorded."""
    meta = _get_meta(vault_path, env)
    return meta.get(key)


def rotate_secret(
    vault_path: str, env: str, key: str, new_value: str, password: str
) -> str:
    """Replace a secret's value and record the rotation timestamp.

    Raises KeyError if the key does not already exist in the given environment.
    Returns the ISO-formatted rotation timestamp.
    """
    existing = get_secret(vault_path, env, key, password)
    if existing is None:
        raise KeyError(f"Key '{key}' not found in env '{env}'. Use 'set' to create it.")

    set_secret(vault_path, env, key, new_value, password)
    return record_rotation(vault_path, env, key)


def list_rotation_info(vault_path: str, env: str) -> dict:
    """Return a mapping of key -> rotation metadata for all tracked keys in env."""
    return dict(_get_meta(vault_path, env))
