"""Track dependencies between secrets (one secret references another)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_dep_path(vault_path: str) -> Path:
    return Path(vault_path).parent / "dependencies.json"


def _load_deps(vault_path: str) -> Dict[str, List[str]]:
    p = _get_dep_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(vault_path: str, data: Dict[str, List[str]]) -> None:
    _get_dep_path(vault_path).write_text(json.dumps(data, indent=2))


def add_dependency(vault_path: str, key: str, depends_on: str) -> List[str]:
    """Record that *key* depends on *depends_on*."""
    if not key or not depends_on:
        raise ValueError("key and depends_on must be non-empty strings")
    if key == depends_on:
        raise ValueError("A secret cannot depend on itself")
    data = _load_deps(vault_path)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save_deps(vault_path, data)
    return deps


def remove_dependency(vault_path: str, key: str, depends_on: str) -> List[str]:
    data = _load_deps(vault_path)
    deps = data.get(key, [])
    deps = [d for d in deps if d != depends_on]
    if deps:
        data[key] = deps
    else:
        data.pop(key, None)
    _save_deps(vault_path, data)
    return deps


def get_dependencies(vault_path: str, key: str) -> List[str]:
    """Return list of keys that *key* depends on."""
    return _load_deps(vault_path).get(key, [])


def get_dependents(vault_path: str, key: str) -> List[str]:
    """Return list of keys that depend on *key*."""
    data = _load_deps(vault_path)
    return [k for k, deps in data.items() if key in deps]


def list_all_dependencies(vault_path: str) -> Dict[str, List[str]]:
    return _load_deps(vault_path)
