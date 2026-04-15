"""CLI commands for secret tagging."""

from __future__ import annotations

import click

from envault.tag import add_tag, remove_tag, get_tags, list_by_tag, clear_tags


@click.group(name="tag")
def tag_cmd():
    """Manage tags on secrets."""


@tag_cmd.command(name="add")
@click.argument("key")
@click.argument("tag")
@click.option("--env", default="default", show_default=True, help="Environment name.")
@click.option("--vault", default="vault.json", show_default=True, envvar="ENVAULT_PATH")
def add_cmd(key: str, tag: str, env: str, vault: str):
    """Add TAG to KEY in ENV."""
    tags = add_tag(vault, env, key, tag)
    click.echo(f"Tags for {key}: {', '.join(tags)}")


@tag_cmd.command(name="remove")
@click.argument("key")
@click.argument("tag")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default="vault.json", show_default=True, envvar="ENVAULT_PATH")
def remove_cmd(key: str, tag: str, env: str, vault: str):
    """Remove TAG from KEY in ENV."""
    remaining = remove_tag(vault, env, key, tag)
    if remaining:
        click.echo(f"Tags for {key}: {', '.join(remaining)}")
    else:
        click.echo(f"No tags remaining for {key}.")


@tag_cmd.command(name="list")
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default="vault.json", show_default=True, envvar="ENVAULT_PATH")
def list_cmd(key: str, env: str, vault: str):
    """List all tags on KEY in ENV."""
    tags = get_tags(vault, env, key)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags for {key}.")


@tag_cmd.command(name="find")
@click.argument("tag")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default="vault.json", show_default=True, envvar="ENVAULT_PATH")
def find_cmd(tag: str, env: str, vault: str):
    """Find all keys carrying TAG in ENV."""
    keys = list_by_tag(vault, env, tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys found with tag '{tag}'.")


@tag_cmd.command(name="clear")
@click.argument("key")
@click.option("--env", default="default", show_default=True)
@click.option("--vault", default="vault.json", show_default=True, envvar="ENVAULT_PATH")
def clear_cmd(key: str, env: str, vault: str):
    """Remove all tags from KEY in ENV."""
    clear_tags(vault, env, key)
    click.echo(f"All tags cleared from {key}.")
