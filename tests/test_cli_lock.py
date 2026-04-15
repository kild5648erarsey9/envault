"""Tests for the lock CLI commands."""

import pytest
from click.testing import CliRunner

from envault.cli_lock import lock_cmd
from envault.lock import lock_secret


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(lock_cmd, args, obj={"vault_path": tmp_vault})


def test_lock_set_success(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "set", "prod", "API_KEY")
    assert result.exit_code == 0
    assert "Locked 'API_KEY'" in result.output


def test_lock_unset_success(runner, tmp_vault):
    lock_secret(tmp_vault, "prod", "DB_PASS")
    result = _invoke(runner, tmp_vault, "unset", "prod", "DB_PASS")
    assert result.exit_code == 0
    assert "Unlocked 'DB_PASS'" in result.output


def test_lock_unset_not_locked(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "unset", "prod", "GHOST")
    assert result.exit_code == 0
    assert "not locked" in result.output


def test_lock_list_shows_keys(runner, tmp_vault):
    lock_secret(tmp_vault, "staging", "KEY_A")
    lock_secret(tmp_vault, "staging", "KEY_B")
    result = _invoke(runner, tmp_vault, "list", "staging")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_lock_list_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "list", "dev")
    assert result.exit_code == 0
    assert "No locked secrets" in result.output


def test_lock_status_locked(runner, tmp_vault):
    lock_secret(tmp_vault, "prod", "TOKEN")
    result = _invoke(runner, tmp_vault, "status", "prod", "TOKEN")
    assert result.exit_code == 0
    assert "locked" in result.output


def test_lock_status_unlocked(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "status", "prod", "FREE_KEY")
    assert result.exit_code == 0
    assert "unlocked" in result.output
