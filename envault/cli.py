"""CLI entry point for envault."""

import click

from envault.vault import set_secret, get_secret, list_keys, delete_secret
from envault.rotation import rotate_secret, get_rotation_info
from envault.export import export_secrets, SUPPORTED_FORMATS

DEFAULT_VAULT = "vault.enc"


@click.group()
def cli():
    """envault — secure environment secret manager."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option("--password", prompt="Master password")
def set(key, value, env, vault, password):
    """Set a secret KEY to VALUE in the vault."""
    set_secret(vault, password, env, key, value)
    click.echo(f"[{env}] {key} set.")


@cli.command()
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt="Master password", hide_input=True)
def get(key, env, vault, password):
    """Get a secret by KEY from the vault."""
    value = get_secret(vault, password, env, key)
    if value is None:
        click.echo(f"Key '{key}' not found in env '{env}'.")
    else:
        click.echo(value)


@cli.command(name="list")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt="Master password", hide_input=True)
def list_cmd(env, vault, password):
    """List all secret keys in an environment."""
    keys = list_keys(vault, password, env)
    if not keys:
        click.echo(f"No secrets found in env '{env}'.")
    else:
        for k in keys:
            click.echo(k)


@cli.command()
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt="Master password", hide_input=True)
def delete(key, env, vault, password):
    """Delete a secret KEY from the vault."""
    delete_secret(vault, password, env, key)
    click.echo(f"[{env}] {key} deleted.")


@cli.command()
@click.argument("key")
@click.argument("new_value")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt="Master password", hide_input=True)
def rotate(key, new_value, env, vault, password):
    """Rotate a secret KEY to NEW_VALUE and record the rotation."""
    info = rotate_secret(vault, password, env, key, new_value)
    click.echo(f"[{env}] {key} rotated at {info['rotated_at']}.")


@cli.command(name="export")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt="Master password", hide_input=True)
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format.",
)
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
@click.option("--keys", default=None, help="Comma-separated list of keys to export.")
def export_cmd(env, vault, password, fmt, output, keys):
    """Export secrets to dotenv, JSON, or shell format."""
    key_list = [k.strip() for k in keys.split(",")] if keys else None
    result = export_secrets(vault, password, env, fmt=fmt, keys=key_list)
    if output:
        with open(output, "w") as f:
            f.write(result + "\n")
        click.echo(f"Exported to {output}.")
    else:
        click.echo(result)
