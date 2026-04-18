"""CLI commands for secret value history."""
import click
from envault.history import get_history, clear_history, list_history_keys


@click.group("history")
def history_cmd():
    """View and manage secret value history."""


@history_cmd.command("show")
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=".vault", show_default=True)
@click.option("--limit", default=10, show_default=True, help="Max entries to show.")
def show_cmd(key, env, vault, limit):
    """Show value history for a secret KEY."""
    entries = get_history(vault, env, key, limit=limit)
    if not entries:
        click.echo(f"No history found for '{key}' in [{env}].")
        return
    click.echo(f"History for '{key}' in [{env}] (newest last):")
    for e in entries:
        click.echo(f"  {e['recorded_at']}  {e['value']}")


@history_cmd.command("clear")
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=".vault", show_default=True)
@click.confirmation_option(prompt="Clear all history for this key?")
def clear_cmd(key, env, vault):
    """Clear value history for a secret KEY."""
    removed = clear_history(vault, env, key)
    click.echo(f"Cleared {removed} history entries for '{key}' in [{env}].")


@history_cmd.command("keys")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default=".vault", show_default=True)
def keys_cmd(env, vault):
    """List all keys that have recorded history."""
    keys = list_history_keys(vault, env)
    if not keys:
        click.echo(f"No history recorded in [{env}].")
        return
    for k in sorted(keys):
        click.echo(k)
