"""CLI entry point for envault."""

import click
from envault.vault import set_secret, get_secret, list_keys, delete_secret
from envault.rotation import rotate_secret, get_rotation_info
from envault.export import export_secrets
from envault.audit import record_event, get_events, clear_log

DEFAULT_VAULT = "vault.json"


@click.group()
def cli():
    """envault — secure environment secret manager."""
    pass


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True)
def set(key, value, env, vault, password):
    """Set a secret KEY to VALUE in ENV."""
    set_secret(vault, env, key, value, password)
    record_event(vault, "set", key, env)
    click.echo(f"Secret '{key}' set in '{env}'.")


@cli.command()
@click.argument("key")
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True)
def get(key, env, vault, password):
    """Get a secret KEY from ENV."""
    value = get_secret(vault, env, key, password)
    if value is None:
        click.echo(f"Key '{key}' not found in '{env}'.", err=True)
    else:
        record_event(vault, "get", key, env)
        click.echo(value)


@cli.command(name="list")
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
def list_cmd(env, vault):
    """List all secret keys in ENV."""
    keys = list_keys(vault, env)
    if not keys:
        click.echo(f"No secrets found in '{env}'.")
    else:
        for k in keys:
            click.echo(k)


@cli.command()
@click.argument("key")
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True)
def delete(key, env, vault, password):
    """Delete a secret KEY from ENV."""
    delete_secret(vault, env, key, password)
    record_event(vault, "delete", key, env)
    click.echo(f"Secret '{key}' deleted from '{env}'.")


@cli.command()
@click.argument("key")
@click.argument("new_value")
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True)
def rotate(key, new_value, env, vault, password):
    """Rotate a secret KEY to NEW_VALUE in ENV."""
    rotate_secret(vault, env, key, new_value, password)
    record_event(vault, "rotate", key, env)
    click.echo(f"Secret '{key}' rotated in '{env}'.")


@cli.command()
@click.option("--env", default="default", help="Target environment.")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--format", "fmt", default="dotenv", type=click.Choice(["dotenv", "json", "shell"]))
@click.option("--password", prompt=True, hide_input=True)
def export(env, vault, fmt, password):
    """Export all secrets in ENV to stdout."""
    output = export_secrets(vault, env, password, fmt)
    click.echo(output)


@cli.group()
def audit():
    """Audit log commands."""
    pass


@audit.command(name="log")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.option("--key", default=None, help="Filter by key.")
@click.option("--env", default=None, help="Filter by environment.")
@click.option("--action", default=None, help="Filter by action.")
def audit_log(vault, key, env, action):
    """Display the audit log."""
    events = get_events(vault, key=key, env=env, action=action)
    if not events:
        click.echo("No audit events found.")
    else:
        for e in events:
            click.echo(f"{e['timestamp']}  {e['action']:8s}  {e['env']:12s}  {e['key']}  (user: {e['user']})")


@audit.command(name="clear")
@click.option("--vault", default=DEFAULT_VAULT, help="Vault file path.")
@click.confirmation_option(prompt="Clear all audit logs?")
def audit_clear(vault):
    """Clear the audit log."""
    clear_log(vault)
    click.echo("Audit log cleared.")


if __name__ == "__main__":
    cli()
