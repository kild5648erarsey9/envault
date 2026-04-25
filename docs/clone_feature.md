# Clone Feature

The **clone** feature lets you copy secrets from one environment to another — either
one key at a time or in bulk, with optional glob filtering.

## API

### `clone_secret(src_env, dst_env, key, vault_path, password, *, overwrite=False)`

Copies a single secret identified by *key* from *src_env* into *dst_env*.

| Argument | Description |
|---|---|
| `src_env` | Source environment name |
| `dst_env` | Destination environment name |
| `key` | Secret key to clone |
| `vault_path` | Path to the vault file |
| `password` | Encryption password |
| `overwrite` | Replace an existing value in the destination (default `False`) |

Raises `CloneError` when:
- The source key does not exist.
- The destination key already exists and `overwrite=False`.
- The source key is **locked** (see `envault.lock`).

### `clone_env(src_env, dst_env, vault_path, password, *, pattern=None, overwrite=False, skip_locked=False)`

Clones all secrets from *src_env* into *dst_env* and returns a summary dict:

```python
{
    "cloned":  ["KEY_A", "KEY_B"],   # successfully cloned keys
    "skipped": ["LOCKED_KEY"],       # keys skipped due to lock (skip_locked=True)
    "errors":  [{"key": "X", "error": "..."}],  # keys that failed
}
```

| Argument | Description |
|---|---|
| `pattern` | Optional glob string to filter keys, e.g. `"DB_*"` |
| `overwrite` | Overwrite existing keys in the destination |
| `skip_locked` | Silently skip locked keys instead of recording them as errors |

## Example

```python
from envault.clone import clone_env

result = clone_env(
    src_env="staging",
    dst_env="prod",
    vault_path=".envault/vault.db",
    password="my-master-password",
    pattern="DB_*",
    overwrite=False,
    skip_locked=True,
)

print("Cloned:", result["cloned"])
print("Skipped (locked):", result["skipped"])
print("Errors:", result["errors"])
```

## Notes

- Cloning respects **locks**: locked keys in the source environment cannot be
  cloned unless `skip_locked=True` is passed (in which case they appear in the
  `skipped` list).
- Cloning does **not** copy metadata such as tags, TTLs, or policies — only the
  encrypted secret value is transferred.
- Use `overwrite=True` carefully in production environments.
