"""Namespace support: group secrets under logical namespaces."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional

NAMESPACE_FILE = ".namespaces.json"


def _get_ns_path(vault_path: str) -> Path:
    return Path(vault_path).parent / NAMESPACE_FILE


def _load(vault_path: str) -> dict:
    p = _get_ns_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _get_ns_path(vault_path).write_text(json.dumps(data, indent=2))


def assign_namespace(vault_path: str, key: str, namespace: str) -> str:
    """Assign a key to a namespace. Returns the namespace."""
    if not namespace or not namespace.strip():
        raise ValueError("Namespace must be a non-empty string.")
    data = _load(vault_path)
    data[key] = namespace.strip()
    _save(vault_path, data)
    return namespace.strip()


def get_namespace(vault_path: str, key: str) -> Optional[str]:
    """Return the namespace for a key, or None."""
    return _load(vault_path).get(key)


def remove_namespace(vault_path: str, key: str) -> None:
    """Remove namespace assignment for a key."""
    data = _load(vault_path)
    data.pop(key, None)
    _save(vault_path, data)


def list_namespaces(vault_path: str) -> List[str]:
    """Return sorted unique namespace names."""
    return sorted(set(_load(vault_path).values()))


def keys_in_namespace(vault_path: str, namespace: str) -> List[str]:
    """Return sorted keys assigned to a given namespace."""
    data = _load(vault_path)
    return sorted(k for k, v in data.items() if v == namespace)
