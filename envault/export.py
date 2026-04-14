"""Export secrets to various formats (dotenv, JSON, shell)."""

import json
from typing import Optional

from envault.vault import get_secret, list_keys


SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def export_secrets(
    vault_path: str,
    password: str,
    env: str,
    fmt: str = "dotenv",
    keys: Optional[list] = None,
) -> str:
    """Export secrets from a vault environment to a string in the given format.

    Args:
        vault_path: Path to the vault file.
        password: Master password for decryption.
        env: Environment name (e.g. 'production').
        fmt: Output format — 'dotenv', 'json', or 'shell'.
        keys: Optional list of keys to export; exports all if None.

    Returns:
        A string representation of the secrets in the requested format.

    Raises:
        ValueError: If an unsupported format is requested or a key is missing.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    available_keys = list_keys(vault_path, password, env)
    export_keys = keys if keys is not None else available_keys

    missing = [k for k in export_keys if k not in available_keys]
    if missing:
        raise ValueError(f"Keys not found in env '{env}': {missing}")

    secrets = {}
    for key in export_keys:
        value = get_secret(vault_path, password, env, key)
        if value is not None:
            secrets[key] = value

    if fmt == "dotenv":
        return _to_dotenv(secrets)
    elif fmt == "json":
        return _to_json(secrets)
    elif fmt == "shell":
        return _to_shell(secrets)


def _to_dotenv(secrets: dict) -> str:
    lines = []
    for key, value in secrets.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def _to_json(secrets: dict) -> str:
    return json.dumps(secrets, indent=2)


def _to_shell(secrets: dict) -> str:
    lines = []
    for key, value in secrets.items():
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)
