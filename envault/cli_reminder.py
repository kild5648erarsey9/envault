"""CLI commands for managing secret reminders."""

import click
from envault.reminder import set_reminder, get_reminder, delete_reminder, list_reminders


@click.group("reminder")
def reminder_cmd():
    """Manage reminder notes attached to secrets."""


@reminder_cmd.command("set")
@click.argument("env")
@click.argument("key")
@click.argument("note")
@click.pass_context
def set_cmd(ctx, env, key, note):
    """Attach a reminder NOTE to KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    try:
        entry = set_reminder(vault_path, env, key, note)
        click.echo(f"Reminder set for '{key}' in '{env}': {entry['note']}")
    except ValueError as e:
        raise click.ClickException(str(e))


@reminder_cmd.command("get")
@click.argument("env")
@click.argument("key")
@click.pass_context
def get_cmd(ctx, env, key):
    """Show the reminder for KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    entry = get_reminder(vault_path, env, key)
    if entry is None:
        click.echo(f"No reminder set for '{key}' in '{env}'.")
    else:
        click.echo(f"{key}: {entry['note']}  (set {entry['created_at']})")


@reminder_cmd.command("delete")
@click.argument("env")
@click.argument("key")
@click.pass_context
def delete_cmd(ctx, env, key):
    """Remove the reminder for KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    removed = delete_reminder(vault_path, env, key)
    if removed:
        click.echo(f"Reminder for '{key}' removed.")
    else:
        click.echo(f"No reminder found for '{key}' in '{env}'.")


@reminder_cmd.command("list")
@click.argument("env")
@click.pass_context
def list_cmd(ctx, env):
    """List all reminders for ENV."""
    vault_path = ctx.obj["vault_path"]
    reminders = list_reminders(vault_path, env)
    if not reminders:
        click.echo(f"No reminders set for '{env}'.")
        return
    for key, entry in sorted(reminders.items()):
        click.echo(f"  {key}: {entry['note']}")
