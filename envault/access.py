"""Access control: restrict which envs/keys a given role can read or write."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_POLICY_FILE = ".access.json"


def _get_access_path(vault_path: str) -> Path:
    return Path(vault_path) / _POLICY_FILE


def _load_access(vault_path: str) -> Dict:
    p = _get_access_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(vault_path: str, data: Dict) -> None:
    p = _get_access_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_access(vault_path: str, role: str, env: str, keys: List[str], mode: str = "read") -> Dict:
    """Grant *role* access to *keys* in *env* with *mode* ('read' or 'write')."""
    if mode not in ("read", "write"):
        raise ValueError(f"mode must be 'read' or 'write', got {mode!r}")
    data = _load_access(vault_path)
    data.setdefault(role, {})
    data[role].setdefault(env, {"read": [], "write": []})
    existing = set(data[role][env].get(mode, []))
    existing.update(keys)
    data[role][env][mode] = sorted(existing)
    _save_access(vault_path, data)
    return data[role][env]


def get_access(vault_path: str, role: str, env: str) -> Optional[Dict]:
    """Return the access entry for *role* in *env*, or None if not set."""
    data = _load_access(vault_path)
    return data.get(role, {}).get(env)


def revoke_access(vault_path: str, role: str, env: str, keys: List[str], mode: str = "read") -> Dict:
    """Remove *keys* from *role*'s *mode* access in *env*."""
    if mode not in ("read", "write"):
        raise ValueError(f"mode must be 'read' or 'write', got {mode!r}")
    data = _load_access(vault_path)
    entry = data.get(role, {}).get(env, {"read": [], "write": []})
    remaining = [k for k in entry.get(mode, []) if k not in keys]
    entry[mode] = remaining
    data.setdefault(role, {})[env] = entry
    _save_access(vault_path, data)
    return entry


def can_access(vault_path: str, role: str, env: str, key: str, mode: str = "read") -> bool:
    """Return True if *role* may perform *mode* on *key* in *env*."""
    entry = get_access(vault_path, role, env)
    if entry is None:
        return False
    allowed = entry.get(mode, [])
    return "*" in allowed or key in allowed


def list_roles(vault_path: str) -> List[str]:
    """Return all roles that have any access entries."""
    return sorted(_load_access(vault_path).keys())
