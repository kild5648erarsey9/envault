# Template Rendering

The **template** feature lets you inject secrets from the vault directly into
configuration file templates, keeping plain-text credentials out of your
repository.

## Placeholder syntax

Wrap any secret key in double curly braces inside your template file:

```
DATABASE_URL=postgresql://{{ DB_USER }}:{{ DB_PASS }}@{{ DB_HOST }}:{{ PORT }}/mydb
API_KEY={{ API_KEY }}
```

Whitespace inside the braces is optional — `{{KEY}}` and `{{ KEY }}` are both
accepted.

## Python API

### `render_string`

```python
from envault.template import render_string

result = render_string(
    template="host={{ DB_HOST }}",
    vault_path="vault.json",
    env="production",
    password="master-password",
)
```

### `render_file`

Reads a template from disk, substitutes secrets, and optionally writes the
rendered output to a destination path:

```python
from envault.template import render_file

render_file(
    src="config/app.env.tmpl",
    vault_path="vault.json",
    env="production",
    password="master-password",
    dest="config/app.env",
)
```

## Strict mode

By default (`strict=True`) any placeholder that references a key absent from
the vault raises `MissingSecretError`.  Pass `strict=False` to leave unknown
placeholders unchanged in the output — useful for partial substitution
workflows.

## CLI

```
envault template render --env production --vault vault.json \
    --src config/app.env.tmpl --dest config/app.env
```

> **Tip:** Add rendered output files (e.g. `*.env`) to `.gitignore` so
> substituted secrets are never committed.
