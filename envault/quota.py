"""Quota management: limit the number of secrets per environment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.vault import list_keys

_QUOTA_FILE = ".quota.json"


def _get_quota_path(vault_path: str) -> Path:
    return Path(vault_path) / _QUOTA_FILE


def _load_quotas(vault_path: str) -> dict:
    p = _get_quota_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quotas(vault_path: str, data: dict) -> None:
    p = _get_quota_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_quota(vault_path: str, env: str, limit: int) -> int:
    """Set the maximum number of secrets allowed in *env*."""
    if limit < 1:
        raise ValueError("Quota limit must be a positive integer.")
    quotas = _load_quotas(vault_path)
    quotas[env] = limit
    _save_quotas(vault_path, quotas)
    return limit


def get_quota(vault_path: str, env: str) -> Optional[int]:
    """Return the quota for *env*, or None if no quota is set."""
    return _load_quotas(vault_path).get(env)


def delete_quota(vault_path: str, env: str) -> bool:
    """Remove the quota for *env*. Returns True if it existed."""
    quotas = _load_quotas(vault_path)
    if env not in quotas:
        return False
    del quotas[env]
    _save_quotas(vault_path, quotas)
    return True


def list_quotas(vault_path: str) -> dict:
    """Return all configured quotas as {env: limit}."""
    return dict(_load_quotas(vault_path))


def check_quota(vault_path: str, env: str, password: str) -> Optional[str]:
    """Return a warning string if *env* is at or over its quota, else None."""
    limit = get_quota(vault_path, env)
    if limit is None:
        return None
    current = len(list_keys(vault_path, env, password))
    if current >= limit:
        return (
            f"Quota exceeded for env '{env}': "
            f"{current}/{limit} secrets used."
        )
    return None
