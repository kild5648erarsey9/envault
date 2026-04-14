"""Tests for envault.export module."""

import json
import os
import pytest

from envault.vault import set_secret
from envault.export import export_secrets


PASSWORD = "export-test-password"
ENV = "staging"


@pytest.fixture
def tmp_vault(tmp_path):
    vault_path = str(tmp_path / "test_vault.enc")
    set_secret(vault_path, PASSWORD, ENV, "DB_URL", "postgres://localhost/db")
    set_secret(vault_path, PASSWORD, ENV, "API_KEY", "secret123")
    set_secret(vault_path, PASSWORD, ENV, "QUOTE_VAL", 'say "hello"')
    return vault_path


def test_export_dotenv_format(tmp_vault):
    result = export_secrets(tmp_vault, PASSWORD, ENV, fmt="dotenv")
    assert 'DB_URL="postgres://localhost/db"' in result
    assert 'API_KEY="secret123"' in result


def test_export_json_format(tmp_vault):
    result = export_secrets(tmp_vault, PASSWORD, ENV, fmt="json")
    data = json.loads(result)
    assert data["DB_URL"] == "postgres://localhost/db"
    assert data["API_KEY"] == "secret123"


def test_export_shell_format(tmp_vault):
    result = export_secrets(tmp_vault, PASSWORD, ENV, fmt="shell")
    assert "export DB_URL='postgres://localhost/db'" in result
    assert "export API_KEY='secret123'" in result


def test_export_dotenv_escapes_quotes(tmp_vault):
    result = export_secrets(tmp_vault, PASSWORD, ENV, fmt="dotenv")
    assert 'QUOTE_VAL="say \\"hello\\""' in result


def test_export_subset_of_keys(tmp_vault):
    result = export_secrets(tmp_vault, PASSWORD, ENV, fmt="json", keys=["API_KEY"])
    data = json.loads(result)
    assert "API_KEY" in data
    assert "DB_URL" not in data


def test_export_missing_key_raises(tmp_vault):
    with pytest.raises(ValueError, match="Keys not found"):
        export_secrets(tmp_vault, PASSWORD, ENV, fmt="dotenv", keys=["NONEXISTENT"])


def test_export_unsupported_format_raises(tmp_vault):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_secrets(tmp_vault, PASSWORD, ENV, fmt="xml")


def test_export_empty_env_returns_empty_string(tmp_path):
    vault_path = str(tmp_path / "empty_vault.enc")
    set_secret(vault_path, PASSWORD, ENV, "SEED", "value")
    result = export_secrets(vault_path, PASSWORD, "empty_env", fmt="dotenv")
    assert result == ""
