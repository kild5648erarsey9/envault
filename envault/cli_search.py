"""CLI commands for searching secrets."""

from __future__ import annotations

import click

from envault.search import search_by_key, search_by_value


@click.group(name="search")
def search_cmd():
    """Search secrets by key pattern or value substring."""


@search_cmd.command(name="key")
@click.argument("pattern")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--env", default=None, help="Restrict to a specific environment.")
def key_cmd(pattern: str, vault: str, password: str, env: str | None):
    """Search secrets by key glob PATTERN (e.g. 'DB_*')."""
    results = search_by_key(vault, password, pattern, env=env)
    if not results:
        click.echo("No matches found.")
        return
    for r in results:
        click.echo(f"{r['env']}  {r['key']}")


@search_cmd.command(name="value")
@click.argument("substring")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--env", default=None, help="Restrict to a specific environment.")
def value_cmd(substring: str, vault: str, password: str, env: str | None):
    """Search secrets whose decrypted value contains SUBSTRING."""
    results = search_by_value(vault, password, substring, env=env)
    if not results:
        click.echo("No matches found.")
        return
    for r in results:
        click.echo(f"{r['env']}  {r['key']}")
