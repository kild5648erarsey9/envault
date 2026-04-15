"""Audit log for tracking secret access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = ".envault_audit.json"


def _get_audit_path(vault_path: str) -> Path:
    base = Path(vault_path).parent
    return base / AUDIT_FILENAME


def _load_log(vault_path: str) -> list:
    audit_path = _get_audit_path(vault_path)
    if not audit_path.exists():
        return []
    with open(audit_path, "r") as f:
        return json.load(f)


def _save_log(vault_path: str, log: list) -> None:
    audit_path = _get_audit_path(vault_path)
    with open(audit_path, "w") as f:
        json.dump(log, f, indent=2)


def record_event(
    vault_path: str,
    action: str,
    key: str,
    env: str,
    user: Optional[str] = None,
) -> dict:
    """Append an audit event and return the event dict."""
    log = _load_log(vault_path)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "env": env,
        "user": user or os.environ.get("USER", "unknown"),
    }
    log.append(event)
    _save_log(vault_path, log)
    return event


def get_events(
    vault_path: str,
    key: Optional[str] = None,
    env: Optional[str] = None,
    action: Optional[str] = None,
) -> list:
    """Return audit events, optionally filtered by key, env, or action."""
    log = _load_log(vault_path)
    results = log
    if key:
        results = [e for e in results if e.get("key") == key]
    if env:
        results = [e for e in results if e.get("env") == env]
    if action:
        results = [e for e in results if e.get("action") == action]
    return results


def clear_log(vault_path: str) -> None:
    """Remove all audit log entries."""
    _save_log(vault_path, [])
