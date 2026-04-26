"""Merge secrets from one environment into another."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.vault import get_secret, set_secret, list_keys


class MergeError(Exception):
    """Raised when a merge operation cannot be completed."""


def merge_envs(
    src_env: str,
    dst_env: str,
    vault_path: str,
    password: str,
    *,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Merge secrets from *src_env* into *dst_env*.

    Args:
        src_env:    Source environment name.
        dst_env:    Destination environment name.
        vault_path: Path to the vault file.
        password:   Master password used for encryption/decryption.
        overwrite:  When True, existing keys in *dst_env* are overwritten.
                    When False (default), existing keys are skipped.
        keys:       Optional explicit list of keys to merge.  When *None*
                    all keys present in *src_env* are considered.

    Returns:
        A dict mapping each key that was **actually written** to its value.

    Raises:
        MergeError: If *src_env* has no secrets or if *overwrite* is False
                    and every requested key already exists in *dst_env*.
    """
    src_keys = list_keys(vault_path, password, src_env)
    if not src_keys:
        raise MergeError(f"Source environment '{src_env}' has no secrets.")

    candidates = keys if keys is not None else src_keys

    # Validate explicitly requested keys exist in source
    if keys is not None:
        missing = [k for k in keys if k not in src_keys]
        if missing:
            raise MergeError(
                f"Keys not found in '{src_env}': {', '.join(missing)}"
            )

    written: Dict[str, str] = {}
    for key in candidates:
        existing = get_secret(vault_path, password, dst_env, key)
        if existing is not None and not overwrite:
            continue  # skip without error
        value = get_secret(vault_path, password, src_env, key)
        if value is None:
            continue
        set_secret(vault_path, password, dst_env, key, value)
        written[key] = value

    return written


def format_merge_report(written: Dict[str, str], dst_env: str) -> str:
    """Return a human-readable summary of a merge operation."""
    if not written:
        return f"No secrets were written to '{dst_env}' (all keys already exist or source was empty)."
    lines = [f"Merged {len(written)} secret(s) into '{dst_env}':"]
    for key in sorted(written):
        lines.append(f"  {key}")
    return "\n".join(lines)
