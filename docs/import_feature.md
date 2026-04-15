# Secret Import Feature

envault supports importing secrets from external files directly into a vault environment.

## Supported Formats

| Format | Extension | Flag |
|--------|-----------|------|
| dotenv | `.env`    | `dotenv` |
| JSON   | `.json`   | `json` |

The format is **auto-detected** from the file extension when `--fmt` is omitted.

## CLI Usage

```bash
# Import from a .env file into the 'staging' environment
envault import secrets.env --env staging

# Import from a JSON file, overwriting existing keys
envault import config.json --env prod --overwrite

# Explicitly specify format
envault import myfile --fmt dotenv --env dev

# Use a custom vault path
envault import secrets.env --vault /etc/myapp/vault.json --env prod
```

## Behaviour

- **Skip by default**: if a key already exists in the target environment it is skipped unless `--overwrite` is passed.
- **Return summary**: the command prints how many secrets were imported and how many were skipped.
- **Password**: read from `ENVAULT_PASSWORD` env var or prompted interactively.
- **Vault path**: defaults to `vault.json`; override with `--vault` or `ENVAULT_VAULT`.

## dotenv Parsing Rules

- Lines starting with `#` and blank lines are ignored.
- Values may be wrapped in single or double quotes (quotes are stripped).
- Escaped sequences `\n` and `\"` inside double-quoted values are unescaped.
- Keys must match `[A-Za-z_][A-Za-z0-9_]*`.

## JSON Parsing Rules

- The top-level value must be a JSON **object** (dict).
- All values are coerced to strings.

## Python API

```python
from envault.import_ import import_secrets

imported, skipped = import_secrets(
    vault_path="vault.json",
    env="production",
    password="s3cr3t",
    source="secrets.env",
    fmt=None,        # auto-detect
    overwrite=False,
)
print(f"{imported} imported, {skipped} skipped")
```
