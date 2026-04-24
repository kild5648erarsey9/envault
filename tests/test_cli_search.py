"""CLI tests for envault search commands."""

import pytest
from click.testing import CliRunner

from envault.cli_search import search_cmd
from envault.vault import set_secret

PASSWORD = "hunter2"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_vault(tmp_path):
    path = str(tmp_path / "vault.json")
    set_secret(path, PASSWORD, "prod", "DB_HOST", "db.prod.example.com")
    set_secret(path, PASSWORD, "prod", "DB_PASSWORD", "s3cr3t")
    set_secret(path, PASSWORD, "staging", "API_KEY", "key-xyz")
    return path


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(
        search_cmd,
        ["--vault", tmp_vault, "--password", PASSWORD, *args],
        catch_exceptions=False,
    )


def test_search_key_finds_matches(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "key", "DB_*")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PASSWORD" in result.output


def test_search_key_no_match_message(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "key", "GHOST_*")
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_search_key_restricted_env(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "key", "DB_*", "--env", "prod")
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" not in result.output


def test_search_value_finds_match(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "value", "example.com")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_search_value_no_match(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "value", "NOTHERE")
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_search_value_restricted_env(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "value", "key-xyz", "--env", "staging")
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "prod" not in result.output


def test_search_key_wrong_password(runner, tmp_vault):
    """Searching with an incorrect password should exit with a non-zero code."""
    result = runner.invoke(
        search_cmd,
        ["--vault", tmp_vault, "--password", "wrongpassword", "key", "DB_*"],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
