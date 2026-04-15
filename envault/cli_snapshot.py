"""CLI commands for snapshot management."""

import click
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot


@click.group("snapshot")
def snapshot_cmd():
    """Create and restore environment snapshots."""


@snapshot_cmd.command("create")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
@click.option("--env", default="default", show_default=True, help="Environment name.")
@click.option("--label", default=None, help="Optional snapshot label (auto-generated if omitted).")
@click.password_option("--password", prompt="Vault password", help="Encryption password.")
def create_cmd(vault, env, label, password):
    """Snapshot all secrets in ENV."""
    label = create_snapshot(vault, env, password, label=label)
    click.echo(f"Snapshot created: {label}")


@snapshot_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
@click.option("--env", default="default", show_default=True, help="Environment name.")
def list_cmd(vault, env):
    """List available snapshots for ENV."""
    snaps = list_snapshots(vault, env)
    if not snaps:
        click.echo(f"No snapshots found for env '{env}'.")
        return
    click.echo(f"{'LABEL':<30} {'CREATED AT':<28} KEYS")
    click.echo("-" * 65)
    for s in snaps:
        click.echo(f"{s['label']:<30} {s['created_at']:<28} {s['key_count']}")


@snapshot_cmd.command("restore")
@click.argument("label")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
@click.option("--env", default="default", show_default=True, help="Environment name.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.password_option("--password", prompt="Vault password", help="Encryption password.")
def restore_cmd(label, vault, env, overwrite, password):
    """Restore secrets from snapshot LABEL into ENV."""
    try:
        written = restore_snapshot(vault, env, password, label, overwrite=overwrite)
        click.echo(f"Restored {written} secret(s) from snapshot '{label}'.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
