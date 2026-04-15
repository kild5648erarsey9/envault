"""CLI commands for importing secrets into envault."""

import click

from envault.import_ import import_secrets


@click.command("import")
@click.argument("source", type=click.Path(exists=True, readable=True))
@click.option("--env", default="default", show_default=True, help="Target environment.")
@click.option("--fmt", type=click.Choice(["dotenv", "json"]), default=None,
              help="Input format (auto-detected from extension if omitted).")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys.")
@click.option("--vault", default="vault.json", show_default=True,
              envvar="ENVAULT_VAULT", help="Path to vault file.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD",
                       prompt="Vault password", confirmation_prompt=False,
                       help="Vault encryption password.")
def import_cmd(source, env, fmt, overwrite, vault, password):
    """Import secrets from SOURCE file (.env or .json) into ENV.

    By default existing keys are skipped; use --overwrite to replace them.
    """
    try:
        imported, skipped = import_secrets(
            vault_path=vault,
            env=env,
            password=password,
            source=source,
            fmt=fmt,
            overwrite=overwrite,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Import failed: {exc}") from exc

    click.echo(
        click.style(f"Imported {imported} secret(s)", fg="green")
        + (f", skipped {skipped} existing" if skipped else "")
        + f" into [{env}]."
    )
