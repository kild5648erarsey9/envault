"""Pre/post rotation hooks — register shell commands to run around secret rotation."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_HOOK_FILE = ".envault_hooks.json"


def _get_hook_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _HOOK_FILE


def _load_hooks(vault_path: str) -> dict:
    p = _get_hook_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_hooks(vault_path: str, data: dict) -> None:
    _get_hook_path(vault_path).write_text(json.dumps(data, indent=2))


def set_hook(vault_path: str, key: str, stage: str, command: str) -> dict:
    """Register a hook command for *key* at *stage* ('pre' or 'post')."""
    if stage not in ("pre", "post"):
        raise ValueError(f"stage must be 'pre' or 'post', got {stage!r}")
    if not command.strip():
        raise ValueError("command must not be empty")
    hooks = _load_hooks(vault_path)
    hooks.setdefault(key, {})[stage] = command
    _save_hooks(vault_path, hooks)
    return hooks[key]


def get_hook(vault_path: str, key: str, stage: str) -> Optional[str]:
    """Return the hook command for *key*/*stage*, or None."""
    return _load_hooks(vault_path).get(key, {}).get(stage)


def delete_hook(vault_path: str, key: str, stage: Optional[str] = None) -> None:
    """Remove hook(s) for *key*. If *stage* is None, removes all stages."""
    hooks = _load_hooks(vault_path)
    if key not in hooks:
        return
    if stage is None:
        del hooks[key]
    else:
        hooks[key].pop(stage, None)
        if not hooks[key]:
            del hooks[key]
    _save_hooks(vault_path, hooks)


def list_hooks(vault_path: str) -> dict:
    """Return all registered hooks."""
    return _load_hooks(vault_path)


def run_hook(vault_path: str, key: str, stage: str) -> Optional[int]:
    """Execute the hook command for *key*/*stage*. Returns exit code or None."""
    import subprocess
    cmd = get_hook(vault_path, key, stage)
    if cmd is None:
        return None
    result = subprocess.run(cmd, shell=True)
    return result.returncode
