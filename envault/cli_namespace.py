"""CLI commands for namespace management."""
import click
from envault.namespace import (
    assign_namespace, get_namespace, remove_namespace,
    list_namespaces, keys_in_namespace,
)


@click.group("namespace")
def namespace_cmd():
    """Manage secret namespaces."""


@namespace_cmd.command("assign")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def assign_cmd(key, namespace, vault):
    """Assign KEY to NAMESPACE."""
    try:
        ns = assign_namespace(vault, key, namespace)
        click.echo(f"Assigned '{key}' to namespace '{ns}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("get")
@click.argument("key")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def get_cmd(key, vault):
    """Show namespace for KEY."""
    ns = get_namespace(vault, key)
    if ns is None:
        click.echo(f"No namespace assigned to '{key}'.")
    else:
        click.echo(ns)


@namespace_cmd.command("remove")
@click.argument("key")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def remove_cmd(key, vault):
    """Remove namespace assignment for KEY."""
    remove_namespace(vault, key)
    click.echo(f"Removed namespace for '{key}'.")


@namespace_cmd.command("list")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def list_cmd(vault):
    """List all namespaces."""
    namespaces = list_namespaces(vault)
    if not namespaces:
        click.echo("No namespaces defined.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_cmd.command("keys")
@click.argument("namespace")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def keys_cmd(namespace, vault):
    """List keys in NAMESPACE."""
    keys = keys_in_namespace(vault, namespace)
    if not keys:
        click.echo(f"No keys in namespace '{namespace}'.")
    else:
        for k in keys:
            click.echo(k)
