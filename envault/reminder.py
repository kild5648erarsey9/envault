"""Reminder module: attach human-readable reminder notes to secrets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REMINDER_FILE = ".reminders.json"


def _get_reminder_path(vault_path: str, env: str) -> Path:
    return Path(vault_path) / env / REMINDER_FILE


def _load_reminders(vault_path: str, env: str) -> dict:
    path = _get_reminder_path(vault_path, env)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_reminders(vault_path: str, env: str, data: dict) -> None:
    path = _get_reminder_path(vault_path, env)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_reminder(vault_path: str, env: str, key: str, note: str) -> dict:
    """Attach a reminder note to a secret key."""
    if not note or not note.strip():
        raise ValueError("Reminder note must not be empty.")
    reminders = _load_reminders(vault_path, env)
    entry = {
        "note": note.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    reminders[key] = entry
    _save_reminders(vault_path, env, reminders)
    return entry


def get_reminder(vault_path: str, env: str, key: str) -> Optional[dict]:
    """Return the reminder entry for a key, or None if not set."""
    return _load_reminders(vault_path, env).get(key)


def delete_reminder(vault_path: str, env: str, key: str) -> bool:
    """Delete the reminder for a key. Returns True if it existed."""
    reminders = _load_reminders(vault_path, env)
    if key not in reminders:
        return False
    del reminders[key]
    _save_reminders(vault_path, env, reminders)
    return True


def list_reminders(vault_path: str, env: str) -> dict:
    """Return all reminder entries for an environment."""
    return _load_reminders(vault_path, env)
