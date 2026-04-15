"""Tests for the policy CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from envault.cli_policy import policy_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def _invoke(runner, tmp_vault, env, *args):
    return runner.invoke(
        policy_cmd,
        ["--vault", tmp_vault, "--env", env, *args],
        catch_exceptions=False,
    )


def test_set_policy_success(runner, tmp_vault):
    result = runner.invoke(
        policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "DB_PASS", "30"]
    )
    assert result.exit_code == 0
    assert "30 day" in result.output


def test_set_policy_invalid_age(runner, tmp_vault):
    result = runner.invoke(
        policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "DB_PASS", "0"]
    )
    assert result.exit_code != 0
    assert "positive integer" in result.output


def test_get_policy_existing(runner, tmp_vault):
    runner.invoke(
        policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "API_KEY", "60"]
    )
    result = runner.invoke(
        policy_cmd, ["get", "--vault", tmp_vault, "--env", "prod", "API_KEY"]
    )
    assert result.exit_code == 0
    assert "max_age_days=60" in result.output


def test_get_policy_missing(runner, tmp_vault):
    result = runner.invoke(
        policy_cmd, ["get", "--vault", tmp_vault, "--env", "prod", "GHOST"]
    )
    assert result.exit_code == 0
    assert "No policy" in result.output


def test_delete_policy(runner, tmp_vault):
    runner.invoke(
        policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "TOKEN", "45"]
    )
    result = runner.invoke(
        policy_cmd, ["delete", "--vault", tmp_vault, "--env", "prod", "TOKEN"]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_policies(runner, tmp_vault):
    runner.invoke(policy_cmd, ["set", "--vault", tmp_vault, "--env", "staging", "A", "10"])
    runner.invoke(policy_cmd, ["set", "--vault", tmp_vault, "--env", "staging", "B", "20"])
    result = runner.invoke(
        policy_cmd, ["list", "--vault", tmp_vault, "--env", "staging"]
    )
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_check_no_violations(runner, tmp_vault):
    runner.invoke(policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "KEY", "30"])
    recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    with patch("envault.policy.get_rotation_info", return_value={"last_rotated": recent}):
        result = runner.invoke(
            policy_cmd, ["check", "--vault", tmp_vault, "--env", "prod"]
        )
    assert result.exit_code == 0
    assert "within policy" in result.output


def test_check_with_violations_exits_nonzero(runner, tmp_vault):
    runner.invoke(policy_cmd, ["set", "--vault", tmp_vault, "--env", "prod", "OLD", "7"])
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    with patch("envault.policy.get_rotation_info", return_value={"last_rotated": old}):
        result = runner.invoke(
            policy_cmd, ["check", "--vault", tmp_vault, "--env", "prod"]
        )
    assert result.exit_code != 0
    assert "OLD" in result.output
