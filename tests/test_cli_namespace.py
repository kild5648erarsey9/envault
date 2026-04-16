import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from envault.cli_namespace import namespace_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(json.dumps({}))
    return str(vault_file)


def _invoke(runner, tmp_vault, *args):
    return runner.invoke(namespace_cmd, ["--vault", tmp_vault, *args])


def test_assign_success(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "assign", "DB_PASS", "database")
    assert result.exit_code == 0
    assert "database" in result.output


def test_assign_empty_namespace_fails(runner, tmp_vault):
    result = runner.invoke(namespace_cmd, ["assign", "KEY", "", "--vault", tmp_vault])
    assert result.exit_code != 0 or "Error" in result.output


def test_get_assigned_namespace(runner, tmp_vault):
    _invoke(runner, tmp_vault, "assign", "API_KEY", "api")
    result = _invoke(runner, tmp_vault, "get", "API_KEY")
    assert result.exit_code == 0
    assert "api" in result.output


def test_get_unassigned_key(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "get", "MISSING")
    assert result.exit_code == 0
    assert "No namespace" in result.output


def test_remove_namespace(runner, tmp_vault):
    _invoke(runner, tmp_vault, "assign", "KEY", "infra")
    result = _invoke(runner, tmp_vault, "remove", "KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_list_namespaces(runner, tmp_vault):
    _invoke(runner, tmp_vault, "assign", "A", "db")
    _invoke(runner, tmp_vault, "assign", "B", "infra")
    result = _invoke(runner, tmp_vault, "list")
    assert "db" in result.output
    assert "infra" in result.output


def test_list_namespaces_empty(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "list")
    assert "No namespaces" in result.output


def test_keys_in_namespace(runner, tmp_vault):
    _invoke(runner, tmp_vault, "assign", "DB_PASS", "database")
    _invoke(runner, tmp_vault, "assign", "DB_USER", "database")
    result = _invoke(runner, tmp_vault, "keys", "database")
    assert "DB_PASS" in result.output
    assert "DB_USER" in result.output


def test_keys_in_empty_namespace(runner, tmp_vault):
    result = _invoke(runner, tmp_vault, "keys", "ghost")
    assert "No keys" in result.output
