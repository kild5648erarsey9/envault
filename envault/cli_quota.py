"""CLI commands for quota management."""

from __future__ import annotations

import click

from envault.quota import check_quota, delete_quota, get_quota, list_quotas, set_quota


@click.group("quota")
def quota_cmd():
    """Manage per-environment secret quotas."""


@quota_cmd.command("set")
@click.argument("env")
@click.argument("limit", type=int)
@click.pass_context
def set_cmd(ctx, env: str, limit: int):
    """Set the maximum number of secrets for ENV."""
    vault_path = ctx.obj["vault_path"]
    try:
        result = set_quota(vault_path, env, limit)
        click.echo(f"Quota for '{env}' set to {result}.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@quota_cmd.command("get")
@click.argument("env")
@click.pass_context
def get_cmd(ctx, env: str):
    """Show the quota for ENV."""
    vault_path = ctx.obj["vault_path"]
    limit = get_quota(vault_path, env)
    if limit is None:
        click.echo(f"No quota set for '{env}'.")
    else:
        click.echo(f"{env}: {limit}")


@quota_cmd.command("delete")
@click.argument("env")
@click.pass_context
def delete_cmd(ctx, env: str):
    """Remove the quota for ENV."""
    vault_path = ctx.obj["vault_path"]
    removed = delete_quota(vault_path, env)
    if removed:
        click.echo(f"Quota for '{env}' removed.")
    else:
        click.echo(f"No quota found for '{env}'.")


@quota_cmd.command("list")
@click.pass_context
def list_cmd(ctx):
    """List all configured quotas."""
    vault_path = ctx.obj["vault_path"]
    quotas = list_quotas(vault_path)
    if not quotas:
        click.echo("No quotas configured.")
        return
    for env, limit in sorted(quotas.items()):
        click.echo(f"{env}: {limit}")


@quota_cmd.command("check")
@click.argument("env")
@click.pass_context
def check_cmd(ctx, env: str):
    """Check whether ENV is within its quota."""
    vault_path = ctx.obj["vault_path"]
    password = ctx.obj["password"]
    warning = check_quota(vault_path, env, password)
    if warning:
        click.echo(warning)
    else:
        click.echo(f"'{env}' is within its quota.")
