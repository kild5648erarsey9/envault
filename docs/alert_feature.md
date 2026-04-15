# Alert Feature

The **alert** module (`envault/alert.py`) inspects secrets against their
configured policies and reports any that are stale or have never been rotated.

## Overview

When a policy is attached to a key (via `envault policy set`), it carries a
`max_age_days` threshold. The alert module compares the last-rotation timestamp
recorded by the rotation module against that threshold and surfaces warnings.

## Public API

### `check_secret(vault_path, password, env, key) -> dict | None`

Checks a single key. Returns `None` if the secret is within policy, or a
warning dict with the following fields:

| Field | Type | Description |
|---|---|---|
| `key` | `str` | The secret key name |
| `env` | `str` | Deployment environment |
| `status` | `str` | `"never_rotated"` or `"expired"` |
| `message` | `str` | Human-readable description |
| `days_since_rotation` | `float \| None` | Age in days (None if never rotated) |
| `max_age_days` | `int` | Configured threshold |

### `check_all(vault_path, password, env) -> list[dict]`

Scans every key that has a policy in the given environment and returns a list
of all warning dicts. Keys without a policy are silently skipped.

## Example

```python
from envault.alert import check_all

warnings = check_all("/path/to/vault.json", "my-password", "production")
for w in warnings:
    print(f"[{w['status'].upper()}] {w['message']}")
```

## Integration with CLI

A future `envault alert` command will call `check_all` and render the results
in a colour-coded table, making it easy to spot secrets that need rotation
before a deployment.

## Design Notes

- The module is **read-only**: it never modifies the vault or policy store.
- Timezone-aware timestamps are handled correctly via `datetime.fromisoformat`.
- Keys that exist in the vault but have **no policy** are ignored, keeping
  the feature opt-in.
