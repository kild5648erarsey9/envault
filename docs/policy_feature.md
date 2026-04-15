# Secret Rotation Policy Feature

Envault supports defining **rotation policies** per secret key per environment.
A policy specifies the maximum number of days allowed between rotations.

## Overview

Rotation policies help enforce security compliance by ensuring secrets are
regularly rotated. When a secret exceeds its policy's `max_age_days`, it is
reported as a **violation**.

## CLI Usage

### Set a policy

```bash
envault policy set --vault vault.enc --env prod DB_PASSWORD 30
# => Policy set: DB_PASSWORD must be rotated every 30 day(s) in [prod]
```

### Get a policy

```bash
envault policy get --vault vault.enc --env prod DB_PASSWORD
# => DB_PASSWORD: max_age_days=30
```

### List all policies

```bash
envault policy list --vault vault.enc --env prod
# => API_KEY: max_age_days=60
# => DB_PASSWORD: max_age_days=30
```

### Delete a policy

```bash
envault policy delete --vault vault.enc --env prod DB_PASSWORD
# => Policy removed for 'DB_PASSWORD' in [prod]
```

### Check for violations

```bash
envault policy check --vault vault.enc --env prod
# => Policy violations in [prod]:
#      API_KEY: last rotated 95 days ago (max 60)
```

The `check` command exits with code `1` if any violations are found, making it
suitable for use in CI/CD pipelines.

## Policy Storage

Policies are stored as a JSON file alongside the vault:

```
.envault_policy_<env>.json
```

This file is separate from the encrypted vault and contains only metadata
(no secret values).

## Integration with Rotation

The `check` command reads last-rotation timestamps from the rotation metadata
(managed by `envault/rotation.py`) and compares them against policy thresholds.

## Environment Variables

| Variable         | Description                         |
|------------------|-------------------------------------|
| `ENVAULT_VAULT`  | Default path to the vault file      |
| `ENVAULT_ENV`    | Default environment name            |
