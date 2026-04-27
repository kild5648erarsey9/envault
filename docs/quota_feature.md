# Quota Feature

The **quota** feature lets you set an upper bound on the number of secrets stored
in any given environment. This is useful for enforcing governance policies and
preventing runaway secret sprawl in shared vaults.

## Core API (`envault/quota.py`)

| Function | Description |
|---|---|
| `set_quota(vault_path, env, limit)` | Set the max secrets allowed in `env`. Raises `ValueError` for non-positive limits. |
| `get_quota(vault_path, env)` | Return the configured limit, or `None` if unset. |
| `delete_quota(vault_path, env)` | Remove the quota. Returns `True` if it existed. |
| `list_quotas(vault_path)` | Return all quotas as `{env: limit}`. |
| `check_quota(vault_path, env, password)` | Return a warning string when the env is at/over its limit, else `None`. |

Quota data is stored in `.quota.json` inside the vault directory.

## CLI (`envault quota`)

```
envault quota set <env> <limit>    # Set quota for an environment
envault quota get <env>            # Display current quota
envault quota delete <env>         # Remove quota
envault quota list                 # List all quotas
envault quota check <env>          # Check if env is within quota
```

### Examples

```bash
# Limit production to 50 secrets
envault quota set production 50

# Check current usage against quota
envault quota check production
# production is within its quota.

# After adding the 51st secret:
envault quota check production
# Quota exceeded for env 'production': 51/50 secrets used.

# List all configured quotas
envault quota list
# dev: 10
# staging: 30
# production: 50
```

## Storage Format

`.quota.json` is a simple JSON object mapping environment names to integer limits:

```json
{
  "dev": 10,
  "staging": 30,
  "production": 50
}
```

## Integration Notes

- `check_quota` is non-destructive — it only reads current state and returns a
  warning string, leaving enforcement to the caller.
- Quotas are independent of encryption; the `.quota.json` file is stored in
  plaintext alongside other metadata files (`.audit.json`, `.policy.json`, etc.).
