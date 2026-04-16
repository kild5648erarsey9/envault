"""CLI commands for managing pre/post rotation hooks."""
import click
from envault.hook import set_hook, get_hook, delete_hook, list_hooks


@click.group("hook")
def hook_cmd():
    """Manage pre/post rotation hooks."""


@hook_cmd.command("set")
@click.argument("key")
@click.argument("stage", type=click.Choice(["pre", "post"]))
@click.argument("command")
@click.option("--vault", default="vault.json", show_default=True)
def set_cmd(key, stage, command, vault):
    """Register a hook COMMAND for KEY at STAGE (pre|post)."""
    try:
        entry = set_hook(vault, key, stage, command)
        click.echo(f"Hook set: [{stage}] {key} -> {entry[stage]}")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@hook_cmd.command("get")
@click.argument("key")
@click.argument("stage", type=click.Choice(["pre", "post"]))
@click.option("--vault", default="vault.json", show_default=True)
def get_cmd(key, stage, vault):
    """Show the hook command for KEY at STAGE."""
    cmd = get_hook(vault, key, stage)
    if cmd is None:
        click.echo(f"No {stage} hook for {key!r}.")
    else:
        click.echo(cmd)


@hook_cmd.command("delete")
@click.argument("key")
@click.option("--stage", type=click.Choice(["pre", "post"]), default=None,
              help="Delete only this stage; omit to delete all.")
@click.option("--vault", default="vault.json", show_default=True)
def delete_cmd(key, stage, vault):
    """Delete hook(s) for KEY."""
    delete_hook(vault, key, stage)
    label = stage or "all stages"
    click.echo(f"Deleted {label} hook(s) for {key!r}.")


@hook_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def list_cmd(vault):
    """List all registered hooks."""
    hooks = list_hooks(vault)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for key, stages in hooks.items():
        for stage, command in stages.items():
            click.echo(f"{key}  [{stage}]  {command}")
