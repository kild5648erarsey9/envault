"""CLI commands for the watermark feature."""

from __future__ import annotations

import click

from envault.watermark import (
    delete_watermark,
    get_watermark,
    list_watermarks,
    set_watermark,
)


@click.group("watermark")
def watermark_cmd():
    """Attach metadata watermarks to secrets."""


@watermark_cmd.command("set")
@click.argument("env")
@click.argument("key")
@click.argument("mark")
@click.option("--vault", default="vault.json", show_default=True)
def set_cmd(env: str, key: str, mark: str, vault: str):
    """Attach MARK to KEY in ENV."""
    try:
        result = set_watermark(vault, env, key, mark)
        click.echo(f"Watermark set: {key} -> {result!r}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@watermark_cmd.command("get")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def get_cmd(env: str, key: str, vault: str):
    """Show the watermark for KEY in ENV."""
    mark = get_watermark(vault, env, key)
    if mark is None:
        click.echo(f"No watermark set for '{key}' in '{env}'.")
    else:
        click.echo(mark)


@watermark_cmd.command("delete")
@click.argument("env")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def delete_cmd(env: str, key: str, vault: str):
    """Remove the watermark for KEY in ENV."""
    removed = delete_watermark(vault, env, key)
    if removed:
        click.echo(f"Watermark removed for '{key}' in '{env}'.")
    else:
        click.echo(f"No watermark found for '{key}' in '{env}'.")


@watermark_cmd.command("list")
@click.argument("env")
@click.option("--vault", default="vault.json", show_default=True)
def list_cmd(env: str, vault: str):
    """List all watermarks in ENV."""
    marks = list_watermarks(vault, env)
    if not marks:
        click.echo(f"No watermarks in '{env}'.")
        return
    for key, mark in sorted(marks.items()):
        click.echo(f"  {key}: {mark}")
