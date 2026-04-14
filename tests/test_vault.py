"""Tests for the vault storage module."""

import json
import pytest
from pathlib import Path

from envault.vault import set_secret, get_secret, list_keys, delete_secret

PASSWORD = "vault-test-password"


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path / "vault.json"


def test_set_and_get_secret(tmp_vault):
    set_secret("production", "DB_URL", "postgres://localhost/db", PASSWORD, tmp_vault)
    value = get_secret("production", "DB_URL", PASSWORD, tmp_vault)
    assert value == "postgres://localhost/db"


def test_get_missing_secret_returns_none(tmp_vault):
    result = get_secret("staging", "MISSING_KEY", PASSWORD, tmp_vault)
    assert result is None


def test_list_keys(tmp_vault):
    set_secret("dev", "API_KEY", "abc123", PASSWORD, tmp_vault)
    set_secret("dev", "SECRET_TOKEN", "xyz789", PASSWORD, tmp_vault)
    keys = list_keys("dev", tmp_vault)
    assert set(keys) == {"API_KEY", "SECRET_TOKEN"}


def test_list_keys_empty_env(tmp_vault):
    assert list_keys("nonexistent", tmp_vault) == []


def test_delete_secret(tmp_vault):
    set_secret("production", "OLD_KEY", "value", PASSWORD, tmp_vault)
    removed = delete_secret("production", "OLD_KEY", tmp_vault)
    assert removed is True
    assert get_secret("production", "OLD_KEY", PASSWORD, tmp_vault) is None


def test_delete_nonexistent_secret(tmp_vault):
    removed = delete_secret("production", "GHOST_KEY", tmp_vault)
    assert removed is False


def test_vault_file_is_valid_json(tmp_vault):
    set_secret("qa", "STRIPE_KEY", "sk_test_123", PASSWORD, tmp_vault)
    with tmp_vault.open() as f:
        data = json.load(f)
    assert "qa" in data
    assert "STRIPE_KEY" in data["qa"]
    # Value should be encrypted, not plaintext
    assert data["qa"]["STRIPE_KEY"] != "sk_test_123"
