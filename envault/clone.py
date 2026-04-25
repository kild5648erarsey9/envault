"""Clone secrets between environments, optionally filtering by key pattern."""

from __future__ import annotations

import fnmatch
from typing import Optional

from envault.vault import get_secret, set_secret, list_keys
from envault.lock import is_locked


class CloneError(Exception):
    """Raised when a clone operation cannot be completed."""


def clone_secret(
    src_env: str,
    dst_env: str,
    key: str,
    vault_path: str,
    password: str,
    *,
    overwrite: bool = False,
) -> str:
    """Copy a single secret from *src_env* to *dst_env*.

    Returns the key that was cloned.
    Raises CloneError if the source key is missing, the destination key already
    exists (and *overwrite* is False), or the source key is locked.
    """
    if is_locked(vault_path, src_env, key):
        raise CloneError(f"Key '{key}' in env '{src_env}' is locked and cannot be cloned.")

    value = get_secret(vault_path, src_env, key, password)
    if value is None:
        raise CloneError(f"Key '{key}' not found in env '{src_env}'.")

    existing = get_secret(vault_path, dst_env, key, password)
    if existing is not None and not overwrite:
        raise CloneError(
            f"Key '{key}' already exists in env '{dst_env}'. Use overwrite=True to replace it."
        )

    set_secret(vault_path, dst_env, key, value, password)
    return key


def clone_env(
    src_env: str,
    dst_env: str,
    vault_path: str,
    password: str,
    *,
    pattern: Optional[str] = None,
    overwrite: bool = False,
    skip_locked: bool = False,
) -> dict:
    """Clone all (or filtered) secrets from *src_env* into *dst_env*.

    *pattern* is an optional glob string applied to key names (e.g. ``"DB_*"``).
    Returns a dict with keys ``cloned``, ``skipped``, and ``errors``.
    """
    keys = list_keys(vault_path, src_env, password)
    if pattern:
        keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]

    cloned, skipped, errors = [], [], []

    for key in keys:
        try:
            clone_secret(
                src_env, dst_env, key, vault_path, password, overwrite=overwrite
            )
            cloned.append(key)
        except CloneError as exc:
            if skip_locked and "locked" in str(exc):
                skipped.append(key)
            else:
                errors.append({"key": key, "error": str(exc)})

    return {"cloned": cloned, "skipped": skipped, "errors": errors}
