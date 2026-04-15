"""Tests for envault.search."""

import pytest

from envault.vault import set_secret
from envault.search import search_by_key, search_by_value

PASSWORD = "hunter2"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _seed(vault_path):
    set_secret(vault_path, PASSWORD, "prod", "DB_HOST", "db.prod.example.com")
    set_secret(vault_path, PASSWORD, "prod", "DB_PASSWORD", "s3cr3t")
    set_secret(vault_path, PASSWORD, "prod", "API_KEY", "key-abc")
    set_secret(vault_path, PASSWORD, "staging", "DB_HOST", "db.staging.example.com")
    set_secret(vault_path, PASSWORD, "staging", "CACHE_URL", "redis://localhost")


# --- search_by_key ---

def test_search_by_key_glob_prefix(tmp_vault):
    _seed(tmp_vault)
    results = search_by_key(tmp_vault, PASSWORD, "DB_*")
    keys = [(r["env"], r["key"]) for r in results]
    assert ("prod", "DB_HOST") in keys
    assert ("prod", "DB_PASSWORD") in keys
    assert ("staging", "DB_HOST") in keys


def test_search_by_key_no_match(tmp_vault):
    _seed(tmp_vault)
    results = search_by_key(tmp_vault, PASSWORD, "NONEXISTENT_*")
    assert results == []


def test_search_by_key_restricted_to_env(tmp_vault):
    _seed(tmp_vault)
    results = search_by_key(tmp_vault, PASSWORD, "DB_*", env="prod")
    envs = {r["env"] for r in results}
    assert envs == {"prod"}


def test_search_by_key_exact_match(tmp_vault):
    _seed(tmp_vault)
    results = search_by_key(tmp_vault, PASSWORD, "API_KEY")
    assert len(results) == 1
    assert results[0] == {"env": "prod", "key": "API_KEY"}


def test_search_by_key_unknown_env_returns_empty(tmp_vault):
    _seed(tmp_vault)
    results = search_by_key(tmp_vault, PASSWORD, "*", env="ghost")
    assert results == []


# --- search_by_value ---

def test_search_by_value_finds_substring(tmp_vault):
    _seed(tmp_vault)
    results = search_by_value(tmp_vault, PASSWORD, "example.com")
    keys = {r["key"] for r in results}
    assert "DB_HOST" in keys


def test_search_by_value_restricted_to_env(tmp_vault):
    _seed(tmp_vault)
    results = search_by_value(tmp_vault, PASSWORD, "example.com", env="staging")
    envs = {r["env"] for r in results}
    assert envs == {"staging"}


def test_search_by_value_no_match(tmp_vault):
    _seed(tmp_vault)
    results = search_by_value(tmp_vault, PASSWORD, "ZZZNOTHERE")
    assert results == []


def test_search_by_value_partial_substring(tmp_vault):
    _seed(tmp_vault)
    results = search_by_value(tmp_vault, PASSWORD, "redis")
    assert len(results) == 1
    assert results[0]["key"] == "CACHE_URL"
