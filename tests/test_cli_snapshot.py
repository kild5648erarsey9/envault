"""CLI integration tests for snapshot commands."""

import json
import os
import pytest
from click.testing import CliRunner

from envault.cli_snapshot import snapshot_cmd
from envault.vault import set_secret


PASSWORD = "cli-test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _populate(vault_path, env="prod"):
    set_secret(vault_path, env, "KEY1", "value1", PASSWORD)
    set_secret(vault_path, env, "KEY2", "value2", PASSWORD)


def _invoke(runner, args, vault_path, password=PASSWORD):
    full_args = [a.replace("__VAULT__", vault_path) for a in args]
    # Inject password twice for password_option confirmation prompts where needed
    return runner.invoke(snapshot_cmd, full_args, input=f"{password}\n{password}\n")


def test_create_snapshot_success(runner, tmp_vault):
    _populate(tmp_vault)
    result = _invoke(runner, ["create", "--vault", tmp_vault, "--env", "prod", "--label", "v1"], tmp_vault)
    assert result.exit_code == 0
    assert "v1" in result.output


def test_create_snapshot_file_written(runner, tmp_vault):
    _populate(tmp_vault)
    _invoke(runner, ["create", "--vault", tmp_vault, "--env", "prod", "--label", "mysnap"], tmp_vault)
    snap_dir = os.path.join(os.path.dirname(tmp_vault), ".snapshots")
    assert os.path.isfile(os.path.join(snap_dir, "prod__mysnap.json"))


def test_list_snapshots_empty(runner, tmp_vault):
    result = runner.invoke(snapshot_cmd, ["list", "--vault", tmp_vault, "--env", "prod"])
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_list_snapshots_shows_entries(runner, tmp_vault):
    _populate(tmp_vault)
    _invoke(runner, ["create", "--vault", tmp_vault, "--env", "prod", "--label", "snap1"], tmp_vault)
    result = runner.invoke(snapshot_cmd, ["list", "--vault", tmp_vault, "--env", "prod"])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "2" in result.output  # key count


def test_restore_snapshot_success(runner, tmp_vault):
    _populate(tmp_vault)
    _invoke(runner, ["create", "--vault", tmp_vault, "--env", "prod", "--label", "bk"], tmp_vault)
    result = _invoke(
        runner,
        ["restore", "bk", "--vault", tmp_vault, "--env", "prod", "--overwrite"],
        tmp_vault,
    )
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_restore_missing_snapshot_shows_error(runner, tmp_vault):
    result = _invoke(
        runner,
        ["restore", "ghost", "--vault", tmp_vault, "--env", "prod"],
        tmp_vault,
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output
