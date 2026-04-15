"""CLI commands for managing secret rotation policies."""

import click
from envault.policy import (
    set_policy,
    get_policy,
    delete_policy,
    list_policies,
    check_violations,
)


@click.group("policy")
def policy_cmd():
    """Manage secret rotation policies."""


@policy_cmd.command("set")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--env", required=True, envvar="ENVAULT_ENV", help="Environment name")
@click.argument("key")
@click.argument("max_age_days", type=int)
def set_cmd(vault, env, key, max_age_days):
    """Set a rotation policy (max age in days) for KEY."""
    try:
        set_policy(vault, env, key, max_age_days)
        click.echo(f"Policy set: {key} must be rotated every {max_age_days} day(s) in [{env}]")
    except ValueError as e:
        raise click.ClickException(str(e))


@policy_cmd.command("get")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--env", required=True, envvar="ENVAULT_ENV", help="Environment name")
@click.argument("key")
def get_cmd(vault, env, key):
    """Show the rotation policy for KEY."""
    policy = get_policy(vault, env, key)
    if policy is None:
        click.echo(f"No policy set for '{key}' in [{env}]")
    else:
        click.echo(f"{key}: max_age_days={policy['max_age_days']}")


@policy_cmd.command("delete")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--env", required=True, envvar="ENVAULT_ENV", help="Environment name")
@click.argument("key")
def delete_cmd(vault, env, key):
    """Remove the rotation policy for KEY."""
    removed = delete_policy(vault, env, key)
    if removed:
        click.echo(f"Policy removed for '{key}' in [{env}]")
    else:
        click.echo(f"No policy found for '{key}' in [{env}]")


@policy_cmd.command("list")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--env", required=True, envvar="ENVAULT_ENV", help="Environment name")
def list_cmd(vault, env):
    """List all rotation policies for an environment."""
    policies = list_policies(vault, env)
    if not policies:
        click.echo(f"No policies defined for [{env}]")
        return
    for key, policy in sorted(policies.items()):
        click.echo(f"{key}: max_age_days={policy['max_age_days']}")


@policy_cmd.command("check")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--env", required=True, envvar="ENVAULT_ENV", help="Environment name")
def check_cmd(vault, env):
    """Check for policy violations (overdue rotations)."""
    violations = check_violations(vault, env)
    if not violations:
        click.echo(f"All secrets in [{env}] are within policy.")
        return
    click.echo(f"Policy violations in [{env}]:")
    for v in violations:
        click.echo(f"  {v['key']}: {v['reason']}")
    raise SystemExit(1)
