"""CLI tests for the reminder feature."""

import pytest
from click.testing import CliRunner
from envault.cli_reminder import reminder_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(
        reminder_cmd,
        list(args),
        obj={"vault_path": tmp_vault},
        catch_exceptions=False,
    )


def test_set_reminder_success(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "set", "prod", "DB_PASS", "Rotate quarterly")
    assert result.exit_code == 0
    assert "Reminder set" in result.output
    assert "Rotate quarterly" in result.output


def test_get_reminder_after_set(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "prod", "API_KEY", "Check vendor")
    result = _invoke(runner, tmp_vault, "get", "prod", "API_KEY")
    assert result.exit_code == 0
    assert "Check vendor" in result.output


def test_get_reminder_missing(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "get", "prod", "GHOST")
    assert result.exit_code == 0
    assert "No reminder" in result.output


def test_delete_reminder_success(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "prod", "TOKEN", "Temp")
    result = _invoke(runner, tmp_vault, "delete", "prod", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_delete_reminder_not_found(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "delete", "prod", "NOPE")
    assert result.exit_code == 0
    assert "No reminder found" in result.output


def test_list_reminders_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "list", "staging")
    assert result.exit_code == 0
    assert "No reminders" in result.output


def test_list_reminders_shows_all(runner, tmp_vault):
    _invoke(runner, tmp_vault, "set", "prod", "A", "Note A")
    _invoke(runner, tmp_vault, "set", "prod", "B", "Note B")
    result = _invoke(runner, tmp_vault, "list", "prod")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_set_reminder_overwrites_existing(runner, tmp_vault):
    """Setting a reminder on an existing key should replace the previous note."""
    _invoke(runner, tmp_vault, "set", "prod", "DB_PASS", "Original note")
    _invoke(runner, tmp_vault, "set", "prod", "DB_PASS", "Updated note")
    result = _invoke(runner, tmp_vault, "get", "prod", "DB_PASS")
    assert result.exit_code == 0
    assert "Updated note" in result.output
    assert "Original note" not in result.output
