"""Diff module for comparing secrets across environments."""

from typing import Dict, List, Optional, Tuple
from envault.vault import list_keys, get_secret


def _get_env_snapshot(vault_path: str, env: str, password: str) -> Dict[str, str]:
    """Return a dict of all key-value pairs for a given environment."""
    keys = list_keys(vault_path, env)
    snapshot = {}
    for key in keys:
        value = get_secret(vault_path, env, key, password)
        snapshot[key] = value if value is not None else ""
    return snapshot


def diff_envs(
    vault_path: str,
    env_a: str,
    env_b: str,
    password: str,
) -> Dict[str, List[Tuple[str, Optional[str], Optional[str]]]]:
    """
    Compare secrets between two environments.

    Returns a dict with three categories:
      - 'added':   keys present in env_b but not env_a  -> (key, None, value_b)
      - 'removed': keys present in env_a but not env_b  -> (key, value_a, None)
      - 'changed': keys present in both but with different values -> (key, value_a, value_b)
    """
    snap_a = _get_env_snapshot(vault_path, env_a, password)
    snap_b = _get_env_snapshot(vault_path, env_b, password)

    keys_a = set(snap_a.keys())
    keys_b = set(snap_b.keys())

    added = [(k, None, snap_b[k]) for k in sorted(keys_b - keys_a)]
    removed = [(k, snap_a[k], None) for k in sorted(keys_a - keys_b)]
    changed = [
        (k, snap_a[k], snap_b[k])
        for k in sorted(keys_a & keys_b)
        if snap_a[k] != snap_b[k]
    ]

    return {"added": added, "removed": removed, "changed": changed}


def format_diff(
    diff_result: Dict[str, List[Tuple[str, Optional[str], Optional[str]]]],
    env_a: str,
    env_b: str,
    show_values: bool = False,
) -> str:
    """Format diff result as a human-readable string."""
    lines = [f"Diff: {env_a} → {env_b}"]
    lines.append("-" * 40)

    def _val(v: Optional[str]) -> str:
        if v is None:
            return "(none)"
        return v if show_values else "***"

    for key, val_a, val_b in diff_result.get("added", []):
        lines.append(f"  + {key}: {_val(val_b)}")

    for key, val_a, val_b in diff_result.get("removed", []):
        lines.append(f"  - {key}: {_val(val_a)}")

    for key, val_a, val_b in diff_result.get("changed", []):
        lines.append(f"  ~ {key}: {_val(val_a)} → {_val(val_b)}")

    total = sum(len(v) for v in diff_result.values())
    if total == 0:
        lines.append("  (no differences)")

    return "\n".join(lines)
