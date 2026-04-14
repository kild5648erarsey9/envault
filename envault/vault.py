"""Vault storage: read/write encrypted secrets to a JSON file."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_PATH = Path(".envault/vault.json")


def _load_raw(vault_path: Path) -> Dict[str, Dict[str, str]]:
    if not vault_path.exists():
        return {}
    with vault_path.open("r") as f:
        return json.load(f)


def _save_raw(data: Dict[str, Dict[str, str]], vault_path: Path) -> None:
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    with vault_path.open("w") as f:
        json.dump(data, f, indent=2)


def set_secret(
    env: str, key: str, value: str, password: str,
    vault_path: Path = DEFAULT_VAULT_PATH
) -> None:
    """Encrypt and store a secret under a given environment and key."""
    data = _load_raw(vault_path)
    data.setdefault(env, {})
    data[env][key] = encrypt(value, password)
    _save_raw(data, vault_path)


def get_secret(
    env: str, key: str, password: str,
    vault_path: Path = DEFAULT_VAULT_PATH
) -> Optional[str]:
    """Retrieve and decrypt a secret. Returns None if not found."""
    data = _load_raw(vault_path)
    encrypted = data.get(env, {}).get(key)
    if encrypted is None:
        return None
    return decrypt(encrypted, password)


def list_keys(env: str, vault_path: Path = DEFAULT_VAULT_PATH) -> list:
    """List all secret keys for a given environment."""
    data = _load_raw(vault_path)
    return list(data.get(env, {}).keys())


def delete_secret(
    env: str, key: str, vault_path: Path = DEFAULT_VAULT_PATH
) -> bool:
    """Delete a secret. Returns True if it existed."""
    data = _load_raw(vault_path)
    if key in data.get(env, {}):
        del data[env][key]
        _save_raw(data, vault_path)
        return True
    return False
