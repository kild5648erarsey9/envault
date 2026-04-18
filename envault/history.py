"""Secret value history tracking for envault."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _get_history_path(vault_path: str, env: str) -> Path:
    return Path(vault_path) / env / ".history.json"


def _load_history(vault_path: str, env: str) -> dict:
    p = _get_history_path(vault_path, env)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_history(vault_path: str, env: str, data: dict) -> None:
    p = _get_history_path(vault_path, env)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def record_history(vault_path: str, env: str, key: str, value: str) -> dict:
    """Append a value snapshot to the key's history."""
    data = _load_history(vault_path, env)
    entry = {
        "value": value,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault(key, []).append(entry)
    _save_history(vault_path, env, data)
    return entry


def get_history(vault_path: str, env: str, key: str, limit: int = 10) -> list[dict]:
    """Return the last `limit` history entries for a key."""
    data = _load_history(vault_path, env)
    entries = data.get(key, [])
    return entries[-limit:]


def clear_history(vault_path: str, env: str, key: str) -> int:
    """Remove all history for a key. Returns number of entries deleted."""
    data = _load_history(vault_path, env)
    removed = len(data.pop(key, []))
    _save_history(vault_path, env, data)
    return removed


def list_history_keys(vault_path: str, env: str) -> list[str]:
    """Return all keys that have history recorded."""
    return list(_load_history(vault_path, env).keys())
