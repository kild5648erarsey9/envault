"""Tag management for envault secrets.

Allows arbitrary string tags to be attached to secrets within an environment,
enabling grouping, filtering, and documentation of related keys.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_tag_path(vault_path: str, env: str) -> Path:
    base = Path(vault_path).parent
    return base / f".tags_{env}.json"


def _load_tags(vault_path: str, env: str) -> Dict[str, List[str]]:
    path = _get_tag_path(vault_path, env)
    if not path.exists():
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def _save_tags(vault_path: str, env: str, data: Dict[str, List[str]]) -> None:
    path = _get_tag_path(vault_path, env)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def add_tag(vault_path: str, env: str, key: str, tag: str) -> List[str]:
    """Add a tag to a secret key. Returns updated tag list."""
    data = _load_tags(vault_path, env)
    tags = data.get(key, [])
    if tag not in tags:
        tags.append(tag)
    data[key] = tags
    _save_tags(vault_path, env, data)
    return tags


def remove_tag(vault_path: str, env: str, key: str, tag: str) -> List[str]:
    """Remove a tag from a secret key. Returns updated tag list."""
    data = _load_tags(vault_path, env)
    tags = [t for t in data.get(key, []) if t != tag]
    if tags:
        data[key] = tags
    else:
        data.pop(key, None)
    _save_tags(vault_path, env, data)
    return tags


def get_tags(vault_path: str, env: str, key: str) -> List[str]:
    """Return all tags for a given key."""
    return _load_tags(vault_path, env).get(key, [])


def list_by_tag(vault_path: str, env: str, tag: str) -> List[str]:
    """Return all keys that carry the given tag."""
    data = _load_tags(vault_path, env)
    return [k for k, tags in data.items() if tag in tags]


def clear_tags(vault_path: str, env: str, key: str) -> None:
    """Remove all tags from a key."""
    data = _load_tags(vault_path, env)
    data.pop(key, None)
    _save_tags(vault_path, env, data)
