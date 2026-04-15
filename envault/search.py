"""Search secrets by key pattern or value substring across environments."""

from __future__ import annotations

import fnmatch
from typing import List, Dict, Any, Optional

from envault.vault import _load_raw, get_secret


def search_by_key(
    vault_path: str,
    password: str,
    pattern: str,
    env: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return secrets whose keys match a glob pattern.

    Args:
        vault_path: Path to the vault file.
        password:   Master password.
        pattern:    Glob pattern, e.g. "DB_*" or "*SECRET*".
        env:        Restrict search to this environment; None means all envs.

    Returns:
        List of dicts with keys ``env``, ``key``.
    """
    raw = _load_raw(vault_path)
    envs = [env] if env else list(raw.keys())
    results: List[Dict[str, Any]] = []
    for e in envs:
        if e not in raw:
            continue
        for key in raw[e]:
            if fnmatch.fnmatch(key, pattern):
                results.append({"env": e, "key": key})
    return results


def search_by_value(
    vault_path: str,
    password: str,
    substring: str,
    env: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return secrets whose decrypted values contain *substring*.

    Args:
        vault_path: Path to the vault file.
        password:   Master password.
        substring:  Case-sensitive substring to look for.
        env:        Restrict search to this environment; None means all envs.

    Returns:
        List of dicts with keys ``env``, ``key``.
    """
    raw = _load_raw(vault_path)
    envs = [env] if env else list(raw.keys())
    results: List[Dict[str, Any]] = []
    for e in envs:
        if e not in raw:
            continue
        for key in raw[e]:
            value = get_secret(vault_path, password, e, key)
            if value is not None and substring in value:
                results.append({"env": e, "key": key})
    return results
