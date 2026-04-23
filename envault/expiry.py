"""expiry.py – track and check secret expiration dates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _get_expiry_path(vault_path: str, env: str) -> Path:
    return Path(vault_path) / env / "expiry.json"


def _load_expiry(vault_path: str, env: str) -> dict:
    p = _get_expiry_path(vault_path, env)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_expiry(vault_path: str, env: str, data: dict) -> None:
    p = _get_expiry_path(vault_path, env)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_expiry(vault_path: str, env: str, key: str, seconds: int) -> str:
    """Set an expiry for *key* that fires *seconds* from now.

    Returns the ISO-8601 expiry timestamp.
    Raises ValueError if seconds <= 0.
    """
    if seconds <= 0:
        raise ValueError("seconds must be a positive integer")
    data = _load_expiry(vault_path, env)
    expires_at = datetime.now(timezone.utc).replace(microsecond=0)
    from datetime import timedelta
    expires_at = expires_at + timedelta(seconds=seconds)
    iso = expires_at.isoformat()
    data[key] = iso
    _save_expiry(vault_path, env, data)
    return iso


def get_expiry(vault_path: str, env: str, key: str) -> Optional[str]:
    """Return the ISO-8601 expiry string for *key*, or None if not set."""
    return _load_expiry(vault_path, env).get(key)


def delete_expiry(vault_path: str, env: str, key: str) -> bool:
    """Remove the expiry for *key*. Returns True if removed, False if absent."""
    data = _load_expiry(vault_path, env)
    if key not in data:
        return False
    del data[key]
    _save_expiry(vault_path, env, data)
    return True


def is_expired(vault_path: str, env: str, key: str) -> Optional[bool]:
    """Return True/False if expiry is set, or None if no expiry exists."""
    iso = get_expiry(vault_path, env, key)
    if iso is None:
        return None
    expires_at = datetime.fromisoformat(iso)
    return datetime.now(timezone.utc) >= expires_at


def list_expiring(vault_path: str, env: str) -> list[dict]:
    """Return all keys with expiry info, sorted by expiry date ascending."""
    data = _load_expiry(vault_path, env)
    now = datetime.now(timezone.utc)
    result = []
    for key, iso in data.items():
        expires_at = datetime.fromisoformat(iso)
        result.append({
            "key": key,
            "expires_at": iso,
            "expired": now >= expires_at,
        })
    result.sort(key=lambda r: r["expires_at"])
    return result
