"""CLI entry point for envault."""

import getpass
import sys
from pathlib import Path

import click

from envault.vault import set_secret, get_secret, list_keys, delete_secret

DEFAULT_VAULT = Path(".envault/vault.json")


@click.group()
def cli():
    """envault — securely manage environment secrets."""


@cli.command()
@click.argument("env")
@click.argument("key")
@click.argument("value")
def set(env, key, value):
    """Set a secret VALUE for KEY in ENV."""
    password = getpass.getpass("Master password: ")
    set_secret(env, key, value, password, DEFAULT_VAULT)
    click.echo(f"✓ Secret '{key}' stored in [{env}]")


@cli.command()
@click.argument("env")
@click.argument("key")
def get(env, key):
    """Get and print a secret for KEY in ENV."""
    password = getpass.getpass("Master password: ")
    value = get_secret(env, key, password, DEFAULT_VAULT)
    if value is None:
        click.echo(f"✗ Secret '{key}' not found in [{env}]", err=True)
        sys.exit(1)
    click.echo(value)


@cli.command(name="list")
@click.argument("env")
def list_cmd(env):
    """List all secret keys in ENV."""
    keys = list_keys(env, DEFAULT_VAULT)
    if not keys:
        click.echo(f"No secrets found in [{env}]")
    else:
        for k in keys:
            click.echo(f"  {k}")


@cli.command()
@click.argument("env")
@click.argument("key")
def delete(env, key):
    """Delete a secret KEY from ENV."""
    removed = delete_secret(env, key, DEFAULT_VAULT)
    if removed:
        click.echo(f"✓ Secret '{key}' removed from [{env}]")
    else:
        click.echo(f"✗ Secret '{key}' not found in [{env}]", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
