"""CLI commands for managing watermarks on secrets."""

import click
from envault.watermark import set_watermark, get_watermark, delete_watermark, list_watermarks


@click.group(name="watermark")
def watermark_cmd():
    """Manage watermarks on secrets."""


@watermark_cmd.command(name="set")
@click.argument("env")
@click.argument("key")
@click.argument("mark")
@click.option("--vault", default="vault.db", show_default=True, help="Path to vault file.")
def set_cmd(env, key, mark, vault):
    """Attach a watermark MARK to KEY in ENV."""
    result = set_watermark(vault, env, key, mark)
    click.echo(f"Watermark set for '{key}' in '{env}': {result}")


@watermark_cmd.command(name="get")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True, help="Path to vault file.")
def get_cmd(env, key, vault):
    """Retrieve the watermark for KEY in ENV."""
    mark = get_watermark(vault, env, key)
    if mark is None:
        click.echo(f"No watermark found for '{key}' in '{env}'.")
    else:
        click.echo(mark)


@watermark_cmd.command(name="delete")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True, help="Path to vault file.")
def delete_cmd(env, key, vault):
    """Remove the watermark for KEY in ENV."""
    removed = delete_watermark(vault, env, key)
    if removed:
        click.echo(f"Watermark removed for '{key}' in '{env}'.")
    else:
        click.echo(f"No watermark found for '{key}' in '{env}'.")


@watermark_cmd.command(name="list")
@click.argument("env")
@click.option("--vault", default="vault.db", show_default=True, help="Path to vault file.")
def list_cmd(env, vault):
    """List all watermarked secrets in ENV."""
    marks = list_watermarks(vault, env)
    if not marks:
        click.echo(f"No watermarks found in '{env}'.")
    else:
        for key, mark in sorted(marks.items()):
            click.echo(f"{key}: {mark}")
