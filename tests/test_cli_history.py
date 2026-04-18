"""Tests for CLI history commands."""
import pytest
from click.testing import CliRunner
from envault.cli_history import history_cmd
from envault.history import record_history


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(history_cmd, ["--vault", tmp_vault, *args])


def test_show_no_history(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "show", "MISSING", "--env", "prod")
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_show_with_entries(runner, tmp_vault):
    record_history(tmp_vault, "prod", "DB_URL", "postgres://old")
    record_history(tmp_vault, "prod", "DB_URL", "postgres://new")
    result = _invoke(runner, tmp_vault, "show", "DB_URL", "--env", "prod")
    assert result.exit_code == 0
    assert "postgres://old" in result.output
    assert "postgres://new" in result.output


def test_show_limit(runner, tmp_vault):
    for i in range(5):
        record_history(tmp_vault, "prod", "K", f"v{i}")
    result = _invoke(runner, tmp_vault, "show", "K", "--env", "prod", "--limit", "2")
    assert result.exit_code == 0
    assert "v4" in result.output
    assert "v0" not in result.output


def test_clear_cmd(runner, tmp_vault):
    record_history(tmp_vault, "prod", "TOKEN", "abc")
    result = runner.invoke(
        history_cmd,
        ["--vault", tmp_vault, "clear", "TOKEN", "--env", "prod"],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "Cleared 1" in result.output


def test_keys_cmd_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "keys", "--env", "staging")
    assert result.exit_code == 0
    assert "No history" in result.output


def test_keys_cmd_lists_keys(runner, tmp_vault):
    record_history(tmp_vault, "prod", "A", "1")
    record_history(tmp_vault, "prod", "B", "2")
    result = _invoke(runner, tmp_vault, "keys", "--env", "prod")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output
