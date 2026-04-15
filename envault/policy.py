"""Secret rotation policy enforcement for envault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_MAX_AGE_DAYS = 90


def _get_policy_path(vault_path: str, env: str) -> Path:
    base = Path(vault_path).parent
    return base / f".envault_policy_{env}.json"


def _load_policies(vault_path: str, env: str) -> Dict[str, Any]:
    path = _get_policy_path(vault_path, env)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_policies(vault_path: str, env: str, policies: Dict[str, Any]) -> None:
    path = _get_policy_path(vault_path, env)
    with open(path, "w") as f:
        json.dump(policies, f, indent=2)


def set_policy(vault_path: str, env: str, key: str, max_age_days: int) -> Dict[str, Any]:
    """Set a rotation policy for a specific secret key."""
    if max_age_days <= 0:
        raise ValueError("max_age_days must be a positive integer")
    policies = _load_policies(vault_path, env)
    policies[key] = {"max_age_days": max_age_days}
    _save_policies(vault_path, env, policies)
    return policies[key]


def get_policy(vault_path: str, env: str, key: str) -> Optional[Dict[str, Any]]:
    """Retrieve the policy for a key, or None if not set."""
    policies = _load_policies(vault_path, env)
    return policies.get(key)


def delete_policy(vault_path: str, env: str, key: str) -> bool:
    """Remove the policy for a key. Returns True if it existed."""
    policies = _load_policies(vault_path, env)
    if key not in policies:
        return False
    del policies[key]
    _save_policies(vault_path, env, policies)
    return True


def list_policies(vault_path: str, env: str) -> Dict[str, Any]:
    """Return all policies for the given environment."""
    return _load_policies(vault_path, env)


def check_violations(vault_path: str, env: str) -> list:
    """Return keys whose last rotation exceeds their policy max_age_days."""
    from envault.rotation import get_rotation_info
    from datetime import datetime, timezone

    policies = _load_policies(vault_path, env)
    violations = []
    for key, policy in policies.items():
        info = get_rotation_info(vault_path, env, key)
        if info is None:
            violations.append({"key": key, "reason": "never rotated"})
            continue
        last = datetime.fromisoformat(info["last_rotated"])
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - last).days
        if age_days > policy["max_age_days"]:
            violations.append({
                "key": key,
                "reason": f"last rotated {age_days} days ago (max {policy['max_age_days']})",
            })
    return violations
