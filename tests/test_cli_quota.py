"""CLI tests for quota commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_quota import quota_cmd
from envault.vault import set_secret


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def _invoke(runner, tmp_vault, *args, password="pw"):
    return runner.invoke(
        quota_cmd,
        list(args),
        obj={"vault_path": tmp_vault, "password": password},
        catch_exceptions=False,
    )


def test_set_quota_success(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "set", "dev", "10")
    assert result.exit_code == 0
    assert "set to 10" in result.output


def test_set_quota_invalid_limit(runner, tmp_vault):
    result = runner.invoke(
        quota_cmd,
        ["set", "dev", "0"],
        obj={"vault_path": tmp_vault, "password": "pw"},
    )
    assert result.exit_code != 0
    assert "positive integer" in result.output


def test_get_quota_after_set(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "staging", "25")
    result = _invoke(runner, tmp_vault, "get", "staging")
    assert result.exit_code == 0
    assert "25" in result.output


def test_get_quota_missing(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "get", "unknown")
    assert result.exit_code == 0
    assert "No quota" in result.output


def test_delete_quota_success(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "dev", "5")
    result = _invoke(runner, tmp_vault, "delete", "dev")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_delete_quota_missing(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "delete", "ghost")
    assert result.exit_code == 0
    assert "No quota found" in result.output


def test_list_quotas_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "list")
    assert result.exit_code == 0
    assert "No quotas" in result.output


def test_list_quotas_shows_all(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "dev", "5")
    _invoke(runner, tmp_vault, "set", "production", "100")
    result = _invoke(runner, tmp_vault, "list")
    assert "dev: 5" in result.output
    assert "production: 100" in result.output


def test_check_quota_within(runner, tmp_vault):
    set_secret(tmp_vault, "dev", "KEY", "val", "pw")
    _invoke(runner, tmp_vault, "set", "dev", "10")
    result = _invoke(runner, tmp_vault, "check", "dev")
    assert result.exit_code == 0
    assert "within" in result.output


def test_check_quota_exceeded(runner, tmp_vault):
    set_secret(tmp_vault, "dev", "A", "1", "pw")
    set_secret(tmp_vault, "dev", "B", "2", "pw")
    _invoke(runner, tmp_vault, "set", "dev", "1")
    result = _invoke(runner, tmp_vault, "check", "dev")
    assert result.exit_code == 0
    assert "exceeded" in result.output.lower() or "/" in result.output
