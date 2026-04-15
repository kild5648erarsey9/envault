"""Alert module: check secrets against policies and emit expiry/staleness warnings."""

from __future__ import annotations

import datetime
from typing import Any

from envault.policy import get_policy, list_policies
from envault.rotation import get_rotation_info
from envault.vault import list_keys


def _days_since(iso_timestamp: str) -> float:
    """Return the number of days elapsed since *iso_timestamp*."""
    then = datetime.datetime.fromisoformat(iso_timestamp)
    now = datetime.datetime.now(tz=then.tzinfo)
    return (now - then).total_seconds() / 86400


def check_secret(
    vault_path: str,
    password: str,
    env: str,
    key: str,
) -> dict[str, Any] | None:
    """Check a single secret against its policy.

    Returns a warning dict if the secret is stale or missing rotation info,
    or *None* if everything is fine.
    """
    policy = get_policy(vault_path, env, key)
    if policy is None:
        return None

    max_age_days: int = policy["max_age_days"]
    info = get_rotation_info(vault_path, password, env, key)

    if info is None or info.get("last_rotated") is None:
        return {
            "key": key,
            "env": env,
            "status": "never_rotated",
            "message": f"{key} has never been rotated (max age: {max_age_days}d).",
            "days_since_rotation": None,
            "max_age_days": max_age_days,
        }

    days = _days_since(info["last_rotated"])
    if days > max_age_days:
        return {
            "key": key,
            "env": env,
            "status": "expired",
            "message": (
                f"{key} is {days:.1f} days old (max age: {max_age_days}d)."
            ),
            "days_since_rotation": round(days, 2),
            "max_age_days": max_age_days,
        }

    return None


def check_all(
    vault_path: str,
    password: str,
    env: str,
) -> list[dict[str, Any]]:
    """Check every key that has a policy in *env* and return all warnings."""
    warnings: list[dict[str, Any]] = []
    keys_with_policies = {p["key"] for p in list_policies(vault_path, env)}
    for key in keys_with_policies:
        result = check_secret(vault_path, password, env, key)
        if result is not None:
            warnings.append(result)
    return warnings
