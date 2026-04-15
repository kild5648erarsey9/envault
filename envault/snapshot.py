"""Snapshot management: save and restore full environment secret snapshots."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from envault.vault import get_secret, list_keys, set_secret


def _get_snapshot_dir(vault_path: str) -> str:
    """Return the directory where snapshots are stored."""
    base = os.path.dirname(vault_path)
    return os.path.join(base, ".snapshots")


def _snapshot_path(vault_path: str, env: str, label: str) -> str:
    snap_dir = _get_snapshot_dir(vault_path)
    os.makedirs(snap_dir, exist_ok=True)
    return os.path.join(snap_dir, f"{env}__{label}.json")


def create_snapshot(vault_path: str, env: str, password: str, label: Optional[str] = None) -> str:
    """Capture all secrets in *env* and write them to a snapshot file.

    Returns the snapshot label used.
    """
    keys = list_keys(vault_path, env)
    secrets = {k: get_secret(vault_path, env, k, password) for k in keys}

    if label is None:
        label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    payload = {
        "env": env,
        "label": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "secrets": secrets,
    }

    path = _snapshot_path(vault_path, env, label)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)

    return label


def list_snapshots(vault_path: str, env: str) -> list[dict]:
    """Return metadata for all snapshots of *env*, newest first."""
    snap_dir = _get_snapshot_dir(vault_path)
    if not os.path.isdir(snap_dir):
        return []

    results = []
    prefix = f"{env}__"
    for fname in os.listdir(snap_dir):
        if fname.startswith(prefix) and fname.endswith(".json"):
            full = os.path.join(snap_dir, fname)
            with open(full) as fh:
                data = json.load(fh)
            results.append({
                "label": data["label"],
                "created_at": data["created_at"],
                "key_count": len(data["secrets"]),
            })

    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results


def restore_snapshot(vault_path: str, env: str, password: str, label: str, overwrite: bool = False) -> int:
    """Restore secrets from snapshot *label* into *env*.

    Returns the number of secrets written.
    """
    path = _snapshot_path(vault_path, env, label)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Snapshot '{label}' not found for env '{env}'")

    with open(path) as fh:
        payload = json.load(fh)

    written = 0
    for key, value in payload["secrets"].items():
        if not overwrite and get_secret(vault_path, env, key, password) is not None:
            continue
        set_secret(vault_path, env, key, value, password)
        written += 1

    return written
