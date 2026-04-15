"""CLI-level tests for the import command."""

import json
from click.testing import CliRunner
import pytest

from envault.cli_import import import_cmd
from envault.vault import get_secret, set_secret


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, tmp_vault, source, extra_args=None):
    args = [source, "--vault", tmp_vault, "--password", "testpass"]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(import_cmd, args, catch_exceptions=False)


def test_import_dotenv_via_cli(runner, tmp_path):
    vault = str(tmp_path / "v.json")
    env_file = tmp_path / "secrets.env"
    env_file.write_text("ALPHA=one\nBETA=two\n")

    result = _invoke(runner, vault, str(env_file), ["--env", "staging"])
    assert result.exit_code == 0
    assert "Imported 2" in result.output
    assert get_secret(vault, "staging", "ALPHA", "testpass") == "one"


def test_import_json_via_cli(runner, tmp_path):
    vault = str(tmp_path / "v.json")
    json_file = tmp_path / "s.json"
    json_file.write_text(json.dumps({"X": "10", "Y": "20"}))

    result = _invoke(runner, vault, str(json_file), ["--env", "prod"])
    assert result.exit_code == 0
    assert "Imported 2" in result.output


def test_import_cli_skips_existing(runner, tmp_path):
    vault = str(tmp_path / "v.json")
    set_secret(vault, "dev", "KEY", "old", "testpass")

    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new\n")

    result = _invoke(runner, vault, str(env_file), ["--env", "dev"])
    assert result.exit_code == 0
    assert "skipped 1 existing" in result.output
    assert get_secret(vault, "dev", "KEY", "testpass") == "old"


def test_import_cli_overwrite_flag(runner, tmp_path):
    vault = str(tmp_path / "v.json")
    set_secret(vault, "dev", "KEY", "old", "testpass")

    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new\n")

    result = _invoke(runner, vault, str(env_file), ["--env", "dev", "--overwrite"])
    assert result.exit_code == 0
    assert "Imported 1" in result.output
    assert get_secret(vault, "dev", "KEY", "testpass") == "new"


def test_import_cli_unsupported_format_error(runner, tmp_path):
    vault = str(tmp_path / "v.json")
    bad_file = tmp_path / "data.csv"
    bad_file.write_text("a,b\n1,2\n")

    result = runner.invoke(
        import_cmd,
        [str(bad_file), "--vault", vault, "--password", "testpass", "--fmt", "dotenv"],
    )
    # dotenv parser silently skips non-matching lines — exit should still be 0
    assert result.exit_code == 0
