"""Watermark support — attach arbitrary metadata strings to secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _get_watermark_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".watermarks.json"


def _load_watermarks(vault_path: str) -> dict:
    p = _get_watermark_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_watermarks(vault_path: str, data: dict) -> None:
    p = _get_watermark_path(vault_path)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_watermark(vault_path: str, env: str, key: str, mark: str) -> str:
    """Attach a watermark string to *key* in *env*.

    Raises ValueError if *mark* is empty or blank.
    """
    mark = mark.strip()
    if not mark:
        raise ValueError("Watermark must not be empty.")
    data = _load_watermarks(vault_path)
    data.setdefault(env, {})[key] = mark
    _save_watermarks(vault_path, data)
    return mark


def get_watermark(vault_path: str, env: str, key: str) -> Optional[str]:
    """Return the watermark for *key* in *env*, or None if not set."""
    data = _load_watermarks(vault_path)
    return data.get(env, {}).get(key)


def delete_watermark(vault_path: str, env: str, key: str) -> bool:
    """Remove the watermark for *key* in *env*.

    Returns True if a watermark was removed, False if none existed.
    """
    data = _load_watermarks(vault_path)
    env_data = data.get(env, {})
    if key not in env_data:
        return False
    del env_data[key]
    if not env_data:
        data.pop(env, None)
    else:
        data[env] = env_data
    _save_watermarks(vault_path, data)
    return True


def list_watermarks(vault_path: str, env: str) -> dict[str, str]:
    """Return all watermarks for *env* as {key: mark}."""
    data = _load_watermarks(vault_path)
    return dict(data.get(env, {}))
