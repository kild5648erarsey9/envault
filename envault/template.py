"""Template rendering: substitute secrets into template strings."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import get_secret

# Matches {{ KEY }} or {{KEY}} with optional whitespace
_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class MissingSecretError(KeyError):
    """Raised when a template references a key that is absent from the vault."""


def render_string(
    template: str,
    vault_path: str,
    env: str,
    password: str,
    *,
    strict: bool = True,
) -> str:
    """Return *template* with every ``{{ KEY }}`` placeholder replaced by the
    corresponding secret value from *vault_path* / *env*.

    Parameters
    ----------
    template:   Raw template string containing ``{{ KEY }}`` placeholders.
    vault_path: Path to the vault file.
    env:        Deployment environment name (e.g. ``"production"``).
    password:   Master password used to decrypt secrets.
    strict:     When *True* (default) raise :exc:`MissingSecretError` for any
                placeholder whose key is not found in the vault.  When *False*
                leave the placeholder unchanged.
    """

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        value = get_secret(vault_path, env, key, password)
        if value is None:
            if strict:
                raise MissingSecretError(
                    f"Secret '{key}' not found in env '{env}'"
                )
            return match.group(0)  # leave placeholder intact
        return value

    return _PATTERN.sub(_replace, template)


def render_file(
    src: str | Path,
    vault_path: str,
    env: str,
    password: str,
    dest: Optional[str | Path] = None,
    *,
    strict: bool = True,
) -> str:
    """Read *src*, render it, and optionally write the result to *dest*.

    Returns the rendered string regardless of whether *dest* is given.
    """
    src = Path(src)
    content = src.read_text(encoding="utf-8")
    rendered = render_string(content, vault_path, env, password, strict=strict)
    if dest is not None:
        Path(dest).write_text(rendered, encoding="utf-8")
    return rendered
