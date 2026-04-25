"""Tests for envault.clone."""

from __future__ import annotations

import pytest

from envault.vault import set_secret, get_secret
from envault.lock import lock_secret
from envault.clone import clone_secret, clone_env, CloneError


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.db")


PASSWORD = "test-password"


def _seed(vault_path, env, **kwargs):
    for k, v in kwargs.items():
        set_secret(vault_path, env, k, v, PASSWORD)


# ---------------------------------------------------------------------------
# clone_secret
# ---------------------------------------------------------------------------

def test_clone_secret_copies_value(tmp_vault):
    _seed(tmp_vault, "staging", API_KEY="abc123")
    clone_secret("staging", "prod", "API_KEY", tmp_vault, PASSWORD)
    assert get_secret(tmp_vault, "prod", "API_KEY", PASSWORD) == "abc123"


def test_clone_secret_missing_key_raises(tmp_vault):
    with pytest.raises(CloneError, match="not found"):
        clone_secret("staging", "prod", "MISSING", tmp_vault, PASSWORD)


def test_clone_secret_existing_no_overwrite_raises(tmp_vault):
    _seed(tmp_vault, "staging", DB_PASS="s3cr3t")
    _seed(tmp_vault, "prod", DB_PASS="old_value")
    with pytest.raises(CloneError, match="already exists"):
        clone_secret("staging", "prod", "DB_PASS", tmp_vault, PASSWORD)


def test_clone_secret_overwrite_replaces_value(tmp_vault):
    _seed(tmp_vault, "staging", DB_PASS="new_value")
    _seed(tmp_vault, "prod", DB_PASS="old_value")
    clone_secret("staging", "prod", "DB_PASS", tmp_vault, PASSWORD, overwrite=True)
    assert get_secret(tmp_vault, "prod", "DB_PASS", PASSWORD) == "new_value"


def test_clone_secret_locked_key_raises(tmp_vault):
    _seed(tmp_vault, "staging", TOKEN="xyz")
    lock_secret(tmp_vault, "staging", "TOKEN")
    with pytest.raises(CloneError, match="locked"):
        clone_secret("staging", "prod", "TOKEN", tmp_vault, PASSWORD)


# ---------------------------------------------------------------------------
# clone_env
# ---------------------------------------------------------------------------

def test_clone_env_copies_all_keys(tmp_vault):
    _seed(tmp_vault, "dev", A="1", B="2", C="3")
    result = clone_env("dev", "qa", tmp_vault, PASSWORD)
    assert sorted(result["cloned"]) == ["A", "B", "C"]
    assert result["errors"] == []
    assert get_secret(tmp_vault, "qa", "A", PASSWORD) == "1"


def test_clone_env_with_glob_pattern(tmp_vault):
    _seed(tmp_vault, "dev", DB_HOST="localhost", DB_PORT="5432", API_KEY="key")
    result = clone_env("dev", "qa", tmp_vault, PASSWORD, pattern="DB_*")
    assert sorted(result["cloned"]) == ["DB_HOST", "DB_PORT"]
    assert get_secret(tmp_vault, "qa", "API_KEY", PASSWORD) is None


def test_clone_env_records_errors_for_existing(tmp_vault):
    _seed(tmp_vault, "dev", X="1", Y="2")
    _seed(tmp_vault, "qa", X="old")
    result = clone_env("dev", "qa", tmp_vault, PASSWORD)
    assert "Y" in result["cloned"]
    assert any(e["key"] == "X" for e in result["errors"])


def test_clone_env_skip_locked(tmp_vault):
    _seed(tmp_vault, "dev", SAFE="ok", SECRET="shh")
    lock_secret(tmp_vault, "dev", "SECRET")
    result = clone_env("dev", "qa", tmp_vault, PASSWORD, skip_locked=True)
    assert "SAFE" in result["cloned"]
    assert "SECRET" in result["skipped"]
    assert result["errors"] == []


def test_clone_env_empty_source(tmp_vault):
    result = clone_env("empty_env", "qa", tmp_vault, PASSWORD)
    assert result == {"cloned": [], "skipped": [], "errors": []}
