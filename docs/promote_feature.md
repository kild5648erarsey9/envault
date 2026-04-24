# Secret Promotion

The **promote** feature lets you copy secrets from one deployment environment
to another (e.g., `staging` → `prod`) without having to re-enter values
manually.

## Core API

### `promote_secret(vault_path, password, key, src_env, dst_env, *, overwrite=False)`

Copies a single key from `src_env` to `dst_env`.

- Raises `PromoteError` if the key is missing in the source environment.
- Raises `PromoteError` if the key already exists in the destination and
  `overwrite=False` (the default).
- Records a `promote` audit event on success.
- Returns the promoted value.

### `promote_all(vault_path, password, src_env, dst_env, *, overwrite=False, exclude=None)`

Promotes **every** key from `src_env` into `dst_env`.

- Keys listed in `exclude` are silently skipped.
- Respects the same `overwrite` semantics as `promote_secret`.
- Returns a `{key: value}` dict of all promoted secrets.

## CLI Usage

```bash
# Promote a single key
envault promote KEY --from staging --to prod

# Promote all keys, replacing existing values
envault promote --all --from staging --to prod --overwrite

# Promote all keys except a few
envault promote --all --from staging --to prod --exclude DEBUG --exclude LOG_LEVEL
```

## Audit Trail

Every successful promotion is recorded in the audit log with action
`"promote"` and a detail string indicating the source environment:

```json
{
  "action": "promote",
  "key": "DB_URL",
  "env": "prod",
  "detail": "promoted from 'staging'",
  "timestamp": "2024-06-01T12:00:00"
}
```

## Notes

- Promotion **does not remove** the secret from the source environment.
- Values are re-encrypted under the destination environment's storage entry;
  the same master password is used for both environments.
