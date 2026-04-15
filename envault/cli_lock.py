"""CLI commands for locking and unlocking secrets."""

import click

from envault.lock import lock_secret, unlock_secret, list_locked, is_locked


@click.group("lock")
def lock_cmd():
    """Lock or unlock secrets to prevent modification."""


@lock_cmd.command("set")
@click.argument("env")
@click.argument("key")
@click.pass_context
def lock_set_cmd(ctx, env: str, key: str):
    """Lock a secret KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    locks = lock_secret(vault_path, env, key)
    click.echo(f"Locked '{key}' in '{env}'. Total locked: {len(locks)}.")


@lock_cmd.command("unset")
@click.argument("env")
@click.argument("key")
@click.pass_context
def lock_unset_cmd(ctx, env: str, key: str):
    """Unlock a secret KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    if not is_locked(vault_path, env, key):
        click.echo(f"'{key}' is not locked in '{env}'.")
        return
    unlock_secret(vault_path, env, key)
    click.echo(f"Unlocked '{key}' in '{env}'.")


@lock_cmd.command("list")
@click.argument("env")
@click.pass_context
def lock_list_cmd(ctx, env: str):
    """List all locked keys in ENV."""
    vault_path = ctx.obj["vault_path"]
    keys = list_locked(vault_path, env)
    if not keys:
        click.echo(f"No locked secrets in '{env}'.")
    else:
        click.echo(f"Locked secrets in '{env}':")
        for k in keys:
            click.echo(f"  {k}")


@lock_cmd.command("status")
@click.argument("env")
@click.argument("key")
@click.pass_context
def lock_status_cmd(ctx, env: str, key: str):
    """Check lock status of KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    status = "locked" if is_locked(vault_path, env, key) else "unlocked"
    click.echo(f"'{key}' in '{env}' is {status}.")
