# Namespace Feature

Namespaces allow you to group related secrets under a logical label (e.g. `database`, `api`, `infra`), making large vaults easier to navigate.

## Storage

Namespace assignments are stored in `.namespaces.json` alongside the vault file. Each entry maps a secret key to a namespace string.

## Python API

```python
from envault.namespace import (
    assign_namespace, get_namespace, remove_namespace,
    list_namespaces, keys_in_namespace,
)

# Assign
assign_namespace("vault.json", "DB_PASSWORD", "database")

# Retrieve
ns = get_namespace("vault.json", "DB_PASSWORD")  # "database"

# List all namespaces
list_namespaces("vault.json")  # ["database", "infra"]

# Keys in a namespace
keys_in_namespace("vault.json", "database")  # ["DB_PASSWORD", "DB_USER"]

# Remove assignment
remove_namespace("vault.json", "DB_PASSWORD")
```

## CLI Usage

```bash
# Assign a key to a namespace
envault namespace assign DB_PASSWORD database --vault vault.json

# Get namespace for a key
envault namespace get DB_PASSWORD --vault vault.json

# Remove namespace assignment
envault namespace remove DB_PASSWORD --vault vault.json

# List all namespaces
envault namespace list --vault vault.json

# List keys in a namespace
envault namespace keys database --vault vault.json
```

## Notes

- Namespace names are trimmed of surrounding whitespace.
- Assigning an empty namespace raises a `ValueError`.
- A key can belong to only one namespace at a time; re-assigning overwrites the previous value.
- Namespaces are independent of environments — the same key across different environments shares one namespace record.
