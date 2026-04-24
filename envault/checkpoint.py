"""Checkpoint: mark a secret's current value as a known-good baseline.

A checkpoint differs from a snapshot in that it is per-key and per-env,
storing only the encrypted value together with a timestamp and an optional
note.  It lets operators quickly verify whether a secret has drifted from
its last approved state.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.vault import get_secret


def _get_checkpoint_dir(vault_path: str) -> Path:
    p = Path(vault_path).parent / ".checkpoints"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _checkpoint_path(vault_path: str, env: str, key: str) -> Path:
    safe_key = key.replace("/", "__")
    return _get_checkpoint_dir(vault_path) / f"{env}__{safe_key}.json"


def create_checkpoint(
    vault_path: str,
    password: str,
    env: str,
    key: str,
    note: Optional[str] = None,
) -> dict:
    """Save the current value of *key* in *env* as a checkpoint.

    Returns the checkpoint record that was persisted.
    Raises KeyError if the secret does not exist.
    """
    value = get_secret(vault_path, password, env, key)
    if value is None:
        raise KeyError(f"Secret '{key}' not found in env '{env}'")

    record = {
        "env": env,
        "key": key,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": note or "",
    }
    _checkpoint_path(vault_path, env, key).write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    return record


def get_checkpoint(
    vault_path: str, env: str, key: str
) -> Optional[dict]:
    """Return the stored checkpoint for *key* in *env*, or None."""
    path = _checkpoint_path(vault_path, env, key)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def delete_checkpoint(vault_path: str, env: str, key: str) -> bool:
    """Delete the checkpoint.  Returns True if it existed, False otherwise."""
    path = _checkpoint_path(vault_path, env, key)
    if path.exists():
        path.unlink()
        return True
    return False


def verify_checkpoint(
    vault_path: str, password: str, env: str, key: str
) -> dict:
    """Compare the live secret value against the stored checkpoint.

    Returns a dict with keys:
      - ``match`` (bool)
      - ``checkpoint`` (dict or None)
      - ``live_value`` (str or None)
    Raises KeyError if no checkpoint exists.
    """
    checkpoint = get_checkpoint(vault_path, env, key)
    if checkpoint is None:
        raise KeyError(f"No checkpoint found for '{key}' in env '{env}'")
    live = get_secret(vault_path, password, env, key)
    return {
        "match": live == checkpoint["value"],
        "checkpoint": checkpoint,
        "live_value": live,
    }
