"""TTL (time-to-live) enforcement for secrets.

Allows setting an expiry duration on a secret so that reads can
detect and optionally reject expired values.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


def _get_ttl_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".ttl.json"


def _load_ttls(vault_path: str) -> dict:
    p = _get_ttl_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttls(vault_path: str, data: dict) -> None:
    _get_ttl_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ttl(vault_path: str, env: str, key: str, seconds: int) -> str:
    """Record an expiry timestamp for *key* in *env*.

    Returns the ISO-formatted expiry time.
    """
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    ttls = _load_ttls(vault_path)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
    ttls.setdefault(env, {})[key] = expires_at
    _save_ttls(vault_path, ttls)
    return expires_at


def get_ttl(vault_path: str, env: str, key: str) -> Optional[str]:
    """Return the raw ISO expiry string, or *None* if no TTL is set."""
    return _load_ttls(vault_path).get(env, {}).get(key)


def delete_ttl(vault_path: str, env: str, key: str) -> bool:
    """Remove TTL for *key*. Returns True if an entry was removed."""
    ttls = _load_ttls(vault_path)
    removed = ttls.get(env, {}).pop(key, None)
    _save_ttls(vault_path, ttls)
    return removed is not None


def is_expired(vault_path: str, env: str, key: str) -> Optional[bool]:
    """Return True/False if a TTL exists, or None if no TTL is set."""
    raw = get_ttl(vault_path, env, key)
    if raw is None:
        return None
    expiry = datetime.fromisoformat(raw)
    return datetime.now(timezone.utc) >= expiry


def check_ttl(vault_path: str, env: str, key: str) -> dict:
    """Return a status dict with keys: has_ttl, expired, expires_at."""
    raw = get_ttl(vault_path, env, key)
    if raw is None:
        return {"has_ttl": False, "expired": None, "expires_at": None}
    expiry = datetime.fromisoformat(raw)
    expired = datetime.now(timezone.utc) >= expiry
    return {"has_ttl": True, "expired": expired, "expires_at": raw}
