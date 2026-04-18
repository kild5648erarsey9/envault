"""CLI commands for alias management."""
import click
from envault.alias import set_alias, get_alias, remove_alias, list_aliases


@click.group("alias")
def alias_cmd():
    """Manage secret key aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("key")
@click.option("--env", default="default", show_default=True, help="Target environment.")
@click.pass_context
def set_cmd(ctx, alias, key, env):
    """Assign ALIAS to KEY in ENV."""
    vault_path = ctx.obj["vault_path"]
    try:
        entry = set_alias(vault_path, alias, key, env)
        click.echo(f"Alias '{alias}' -> {entry['key']} [{entry['env']}]")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("get")
@click.argument("alias")
@click.pass_context
def get_cmd(ctx, alias):
    """Resolve ALIAS to its key and environment."""
    vault_path = ctx.obj["vault_path"]
    entry = get_alias(vault_path, alias)
    if entry is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"{entry['key']} [{entry['env']}]")


@alias_cmd.command("remove")
@click.argument("alias")
@click.pass_context
def remove_cmd(ctx, alias):
    """Delete ALIAS."""
    vault_path = ctx.obj["vault_path"]
    if remove_alias(vault_path, alias):
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("list")
@click.pass_context
def list_cmd(ctx):
    """List all aliases."""
    vault_path = ctx.obj["vault_path"]
    aliases = list_aliases(vault_path)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, entry in sorted(aliases.items()):
        click.echo(f"{alias:20s} -> {entry['key']} [{entry['env']}]")
