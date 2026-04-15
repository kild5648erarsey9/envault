"""Import secrets from external formats (.env, JSON) into a vault environment."""

import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from envault.vault import set_secret


def _parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a key-value dict."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
            value = value.replace('\\n', '\n').replace('\\"', '"')
        result[key] = value
    return result


def _parse_json(content: str) -> Dict[str, str]:
    """Parse a JSON object into a key-value dict (values coerced to str)."""
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON import requires a top-level object/dict")
    return {str(k): str(v) for k, v in data.items()}


def import_secrets(
    vault_path: str,
    env: str,
    password: str,
    source: str,
    fmt: Optional[str] = None,
    overwrite: bool = False,
) -> Tuple[int, int]:
    """Import secrets from *source* file into *env*.

    Returns (imported_count, skipped_count).
    fmt can be 'dotenv' or 'json'; auto-detected from extension if None.
    """
    path = Path(source)
    if fmt is None:
        fmt = "json" if path.suffix.lower() == ".json" else "dotenv"

    content = path.read_text(encoding="utf-8")

    if fmt == "json":
        pairs = _parse_json(content)
    elif fmt == "dotenv":
        pairs = _parse_dotenv(content)
    else:
        raise ValueError(f"Unsupported import format: {fmt}")

    imported = 0
    skipped = 0
    for key, value in pairs.items():
        from envault.vault import get_secret
        existing = get_secret(vault_path, env, key, password)
        if existing is not None and not overwrite:
            skipped += 1
            continue
        set_secret(vault_path, env, key, value, password)
        imported += 1

    return imported, skipped
