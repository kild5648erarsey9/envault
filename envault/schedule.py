"""Schedule-based rotation reminders for secrets."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

VALID_INTERVALS = ("daily", "weekly", "monthly", "quarterly", "yearly")

INTERVAL_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365,
}


def _get_schedule_path(vault_path: str) -> Path:
    return Path(vault_path).parent / "schedules.json"


def _load_schedules(vault_path: str) -> dict:
    p = _get_schedule_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schedules(vault_path: str, data: dict) -> None:
    _get_schedule_path(vault_path).write_text(json.dumps(data, indent=2))


def set_schedule(vault_path: str, env: str, key: str, interval: str) -> dict:
    """Assign a rotation schedule interval to a secret."""
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval '{interval}'. Choose from {VALID_INTERVALS}.")
    data = _load_schedules(vault_path)
    data.setdefault(env, {})[key] = {
        "interval": interval,
        "interval_days": INTERVAL_DAYS[interval],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_schedules(vault_path, data)
    return data[env][key]


def get_schedule(vault_path: str, env: str, key: str) -> Optional[dict]:
    """Return the schedule entry for a secret, or None."""
    return _load_schedules(vault_path).get(env, {}).get(key)


def remove_schedule(vault_path: str, env: str, key: str) -> bool:
    """Remove a schedule. Returns True if it existed."""
    data = _load_schedules(vault_path)
    if key in data.get(env, {}):
        del data[env][key]
        _save_schedules(vault_path, data)
        return True
    return False


def list_schedules(vault_path: str, env: str) -> dict:
    """Return all schedules for an environment."""
    return _load_schedules(vault_path).get(env, {})


def due_for_rotation(vault_path: str, env: str, key: str, last_rotated_iso: Optional[str]) -> bool:
    """Return True if the secret is due for rotation based on its schedule."""
    entry = get_schedule(vault_path, env, key)
    if entry is None:
        return False
    if last_rotated_iso is None:
        return True
    last = datetime.fromisoformat(last_rotated_iso)
    now = datetime.now(timezone.utc)
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (now - last).days >= entry["interval_days"]
