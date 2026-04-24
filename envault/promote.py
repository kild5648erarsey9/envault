"""Promote secrets from one environment to another."""

from __future__ import annotations

from typing import Optional

from envault.vault import get_secret, set_secret, list_keys
from envault.audit import record_event


class PromoteError(Exception):
    """Raised when a promotion cannot be completed."""


def promote_secret(
    vault_path: str,
    password: str,
    key: str,
    src_env: str,
    dst_env: str,
    *,
    overwrite: bool = False,
) -> str:
    """Copy *key* from *src_env* to *dst_env*.

    Returns the promoted value.
    Raises PromoteError if the key is missing in the source or already exists
    in the destination and *overwrite* is False.
    """
    value = get_secret(vault_path, password, src_env, key)
    if value is None:
        raise PromoteError(
            f"Key '{key}' not found in environment '{src_env}'."
        )

    existing = get_secret(vault_path, password, dst_env, key)
    if existing is not None and not overwrite:
        raise PromoteError(
            f"Key '{key}' already exists in environment '{dst_env}'. "
            "Use overwrite=True to replace it."
        )

    set_secret(vault_path, password, dst_env, key, value)
    record_event(
        vault_path,
        "promote",
        key,
        dst_env,
        detail=f"promoted from '{src_env}'",
    )
    return value


def promote_all(
    vault_path: str,
    password: str,
    src_env: str,
    dst_env: str,
    *,
    overwrite: bool = False,
    exclude: Optional[list[str]] = None,
) -> dict[str, str]:
    """Promote every key from *src_env* into *dst_env*.

    Returns a mapping of {key: value} for all promoted secrets.
    Keys listed in *exclude* are skipped.
    """
    exclude = exclude or []
    keys = list_keys(vault_path, password, src_env)
    promoted: dict[str, str] = {}
    for key in keys:
        if key in exclude:
            continue
        value = promote_secret(
            vault_path, password, key, src_env, dst_env, overwrite=overwrite
        )
        promoted[key] = value
    return promoted
