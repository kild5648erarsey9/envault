# envault

> A CLI tool for securely managing and rotating environment secrets across multiple deployment environments.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install envault
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add and retrieve secrets:

```bash
envault set DATABASE_URL "postgres://user:pass@host/db" --env production
envault get DATABASE_URL --env production
envault list --env staging
```

Rotate a secret across environments:

```bash
envault rotate API_KEY --envs staging,production
```

Export secrets to a `.env` file:

```bash
envault export --env production > .env
```

Run a command with secrets injected as environment variables:

```bash
envault run --env production -- python app.py
```

---

## Configuration

Envault stores encrypted secrets locally in `~/.envault/` by default. Use `--config` to specify a custom path.

```bash
envault --config /path/to/config init
```

---

## License

This project is licensed under the [MIT License](LICENSE).