"""CLI commands for managing secret expiry."""

from __future__ import annotations

import click

from envault.expiry import (
    set_expiry,
    get_expiry,
    delete_expiry,
    is_expired,
    list_expiring,
)


@click.group("expiry")
def expiry_cmd():
    """Manage secret expiration dates."""


@expiry_cmd.command("set")
@click.argument("env")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default=".envault", show_default=True)
def set_cmd(env: str, key: str, seconds: int, vault: str):
    """Set an expiry of SECONDS from now for KEY in ENV."""
    try:
        iso = set_expiry(vault, env, key, seconds)
        click.echo(f"Expiry set: {key} expires at {iso}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@expiry_cmd.command("get")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def get_cmd(env: str, key: str, vault: str):
    """Show the expiry timestamp for KEY in ENV."""
    iso = get_expiry(vault, env, key)
    if iso is None:
        click.echo(f"No expiry set for '{key}'")
    else:
        expired = is_expired(vault, env, key)
        status = "EXPIRED" if expired else "active"
        click.echo(f"{key}: {iso}  [{status}]")


@expiry_cmd.command("delete")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def delete_cmd(env: str, key: str, vault: str):
    """Remove the expiry for KEY in ENV."""
    removed = delete_expiry(vault, env, key)
    if removed:
        click.echo(f"Expiry removed for '{key}'")
    else:
        click.echo(f"No expiry found for '{key}'")


@expiry_cmd.command("list")
@click.argument("env")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--expired-only", is_flag=True, default=False)
def list_cmd(env: str, vault: str, expired_only: bool):
    """List all keys with expiry dates in ENV."""
    items = list_expiring(vault, env)
    if expired_only:
        items = [i for i in items if i["expired"]]
    if not items:
        click.echo("No expiry entries found.")
        return
    for item in items:
        status = "EXPIRED" if item["expired"] else "active"
        click.echo(f"{item['key']:<30} {item['expires_at']}  [{status}]")
