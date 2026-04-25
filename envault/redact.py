"""redact.py — mask secret values in output for safe display."""

from __future__ import annotations

import json
import re
from pathlib import Path

_REDACT_STORE: dict[str, set[str]] = {}  # vault_path -> set of keys to redact

_DEFAULT_MASK = "***"
_PARTIAL_MASK_CHARS = 4  # how many trailing chars to reveal in partial mode


def _get_redact_path(vault_path: str) -> Path:
    return Path(vault_path) / ".redact.json"


def _load_redacted(vault_path: str) -> set[str]:
    p = _get_redact_path(vault_path)
    if not p.exists():
        return set()
    return set(json.loads(p.read_text()))


def _save_redacted(vault_path: str, keys: set[str]) -> None:
    p = _get_redact_path(vault_path)
    p.write_text(json.dumps(sorted(keys), indent=2))


def mark_redacted(vault_path: str, key: str) -> list[str]:
    """Mark a key as redacted. Returns updated list of redacted keys."""
    keys = _load_redacted(vault_path)
    keys.add(key)
    _save_redacted(vault_path, keys)
    return sorted(keys)


def unmark_redacted(vault_path: str, key: str) -> list[str]:
    """Remove a key from the redacted list. Returns updated list."""
    keys = _load_redacted(vault_path)
    keys.discard(key)
    _save_redacted(vault_path, keys)
    return sorted(keys)


def is_redacted(vault_path: str, key: str) -> bool:
    """Return True if the key is marked for redaction."""
    return key in _load_redacted(vault_path)


def list_redacted(vault_path: str) -> list[str]:
    """Return sorted list of all redacted keys."""
    return sorted(_load_redacted(vault_path))


def mask_value(value: str, partial: bool = False, mask: str = _DEFAULT_MASK) -> str:
    """Return a masked representation of *value*.

    If *partial* is True, reveal the last ``_PARTIAL_MASK_CHARS`` characters.
    """
    if not value:
        return mask
    if partial and len(value) > _PARTIAL_MASK_CHARS:
        return mask + value[-_PARTIAL_MASK_CHARS:]
    return mask


def redact_text(text: str, secrets: dict[str, str], mask: str = _DEFAULT_MASK) -> str:
    """Replace any occurrence of a secret value inside *text* with *mask*.

    Useful for scrubbing log lines or command output.
    """
    for value in secrets.values():
        if value:
            text = text.replace(value, mask)
    return text
