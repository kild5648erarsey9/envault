"""Group management for envault secrets.

Allows secrets to be organised into named groups within an environment,
enabling bulk operations and logical categorisation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _load_raw


def _get_group_path(vault_path: str, env: str) -> Path:
    base = Path(vault_path).parent
    return base / f".groups_{env}.json"


def _load_groups(vault_path: str, env: str) -> Dict[str, List[str]]:
    path = _get_group_path(vault_path, env)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_groups(vault_path: str, env: str, data: Dict[str, List[str]]) -> None:
    path = _get_group_path(vault_path, env)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_to_group(vault_path: str, env: str, group: str, key: str) -> List[str]:
    """Add *key* to *group*. Returns the updated sorted member list."""
    if not group.strip():
        raise ValueError("Group name must not be empty.")
    groups = _load_groups(vault_path, env)
    members = groups.get(group, [])
    if key not in members:
        members.append(key)
        members.sort()
    groups[group] = members
    _save_groups(vault_path, env, groups)
    return members


def remove_from_group(vault_path: str, env: str, group: str, key: str) -> List[str]:
    """Remove *key* from *group*. Returns the updated member list."""
    groups = _load_groups(vault_path, env)
    members = groups.get(group, [])
    members = [m for m in members if m != key]
    groups[group] = members
    _save_groups(vault_path, env, groups)
    return members


def get_group(vault_path: str, env: str, group: str) -> Optional[List[str]]:
    """Return members of *group*, or None if the group does not exist."""
    groups = _load_groups(vault_path, env)
    return groups.get(group)


def list_groups(vault_path: str, env: str) -> List[str]:
    """Return all group names defined in *env*."""
    return sorted(_load_groups(vault_path, env).keys())


def delete_group(vault_path: str, env: str, group: str) -> bool:
    """Delete *group* entirely. Returns True if it existed, False otherwise."""
    groups = _load_groups(vault_path, env)
    if group not in groups:
        return False
    del groups[group]
    _save_groups(vault_path, env, groups)
    return True


def find_groups_for_key(vault_path: str, env: str, key: str) -> List[str]:
    """Return all groups that contain *key*."""
    groups = _load_groups(vault_path, env)
    return sorted(g for g, members in groups.items() if key in members)
