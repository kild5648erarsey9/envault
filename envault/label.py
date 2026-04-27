"""Label management for secrets — attach human-readable labels to keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_label_path(vault_path: str) -> Path:
    return Path(vault_path) / "_labels.json"


def _load_labels(vault_path: str) -> Dict[str, List[str]]:
    path = _get_label_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_labels(vault_path: str, data: Dict[str, List[str]]) -> None:
    path = _get_label_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def add_label(vault_path: str, env: str, key: str, label: str) -> List[str]:
    """Add a label to a secret key. Duplicates are silently ignored."""
    label = label.strip()
    if not label:
        raise ValueError("Label must not be empty.")
    data = _load_labels(vault_path)
    ns = f"{env}:{key}"
    existing = data.get(ns, [])
    if label not in existing:
        existing.append(label)
    data[ns] = sorted(existing)
    _save_labels(vault_path, data)
    return data[ns]


def remove_label(vault_path: str, env: str, key: str, label: str) -> List[str]:
    """Remove a label from a secret key. No-op if label not present."""
    data = _load_labels(vault_path)
    ns = f"{env}:{key}"
    existing = data.get(ns, [])
    data[ns] = [l for l in existing if l != label]
    _save_labels(vault_path, data)
    return data[ns]


def get_labels(vault_path: str, env: str, key: str) -> List[str]:
    """Return all labels for a secret key."""
    data = _load_labels(vault_path)
    return data.get(f"{env}:{key}", [])


def find_by_label(vault_path: str, env: str, label: str) -> List[str]:
    """Return all keys in an env that have the given label."""
    data = _load_labels(vault_path)
    prefix = f"{env}:"
    return [
        ns[len(prefix):]
        for ns, labels in data.items()
        if ns.startswith(prefix) and label in labels
    ]


def clear_labels(vault_path: str, env: str, key: str) -> None:
    """Remove all labels from a secret key."""
    data = _load_labels(vault_path)
    ns = f"{env}:{key}"
    data.pop(ns, None)
    _save_labels(vault_path, data)
