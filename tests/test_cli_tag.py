"""CLI tests for the tag feature."""

import pytest
from click.testing import CliRunner

from envault.cli_tag import tag_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(tag_cmd, [*args, "--vault", tmp_vault])


def test_add_tag_success(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "add", "DB_URL", "database", "--env", "prod")
    assert result.exit_code == 0
    assert "database" in result.output


def test_add_multiple_tags(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "DB_URL", "database", "--env", "prod")
    result = _invoke(runner, tmp_vault, "add", "DB_URL", "critical", "--env", "prod")
    assert result.exit_code == 0
    assert "database" in result.output
    assert "critical" in result.output


def test_list_tags(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "API_KEY", "auth", "--env", "dev")
    result = _invoke(runner, tmp_vault, "list", "API_KEY", "--env", "dev")
    assert result.exit_code == 0
    assert "auth" in result.output


def test_list_tags_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "list", "MISSING", "--env", "dev")
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_remove_tag(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "SECRET", "sensitive", "--env", "prod")
    _invoke(runner, tmp_vault, "add", "SECRET", "auth", "--env", "prod")
    result = _invoke(runner, tmp_vault, "remove", "SECRET", "sensitive", "--env", "prod")
    assert result.exit_code == 0
    assert "sensitive" not in result.output


def test_remove_last_tag_message(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "SOLO", "only", "--env", "prod")
    result = _invoke(runner, tmp_vault, "remove", "SOLO", "only", "--env", "prod")
    assert result.exit_code == 0
    assert "No tags remaining" in result.output


def test_find_by_tag(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "DB_URL", "infra", "--env", "prod")
    _invoke(runner, tmp_vault, "add", "REDIS_URL", "infra", "--env", "prod")
    result = _invoke(runner, tmp_vault, "find", "infra", "--env", "prod")
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "REDIS_URL" in result.output


def test_find_no_match(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "find", "ghost", "--env", "prod")
    assert result.exit_code == 0
    assert "No keys found" in result.output


def test_clear_tags(runner, tmp_vault):
    _invoke(runner, tmp_vault, "add", "KEY", "t1", "--env", "dev")
    result = _invoke(runner, tmp_vault, "clear", "KEY", "--env", "dev")
    assert result.exit_code == 0
    assert "cleared" in result.output
