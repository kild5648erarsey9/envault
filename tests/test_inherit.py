"""Tests for envault.inherit — secret inheritance between environments."""

import pytest

from envault.inherit import (
    get_parent,
    list_resolved_keys,
    remove_parent,
    resolve_secret,
    set_parent,
)
from envault.vault import set_secret


PASSWORD = "test-pass"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def _seed(vault_path, env, key, value):
    set_secret(vault_path, env, key, value, PASSWORD)


# ---------------------------------------------------------------------------
# set_parent / get_parent / remove_parent
# ---------------------------------------------------------------------------

def test_set_parent_returns_parent_name(tmp_vault):
    result = set_parent(tmp_vault, "staging", "production")
    assert result == "production"


def test_get_parent_after_set(tmp_vault):
    set_parent(tmp_vault, "staging", "production")
    assert get_parent(tmp_vault, "staging") == "production"


def test_get_parent_missing_returns_none(tmp_vault):
    assert get_parent(tmp_vault, "staging") is None


def test_set_parent_self_raises(tmp_vault):
    with pytest.raises(ValueError, match="cannot inherit from itself"):
        set_parent(tmp_vault, "prod", "prod")


def test_remove_parent_clears_link(tmp_vault):
    set_parent(tmp_vault, "staging", "production")
    remove_parent(tmp_vault, "staging")
    assert get_parent(tmp_vault, "staging") is None


def test_remove_parent_nonexistent_is_noop(tmp_vault):
    remove_parent(tmp_vault, "ghost")  # should not raise


# ---------------------------------------------------------------------------
# resolve_secret
# ---------------------------------------------------------------------------

def test_resolve_secret_found_in_own_env(tmp_vault):
    _seed(tmp_vault, "staging", "DB_URL", "staging-db")
    _seed(tmp_vault, "production", "DB_URL", "prod-db")
    set_parent(tmp_vault, "staging", "production")
    assert resolve_secret(tmp_vault, "staging", "DB_URL", PASSWORD) == "staging-db"


def test_resolve_secret_falls_back_to_parent(tmp_vault):
    _seed(tmp_vault, "production", "API_KEY", "prod-key")
    set_parent(tmp_vault, "staging", "production")
    assert resolve_secret(tmp_vault, "staging", "API_KEY", PASSWORD) == "prod-key"


def test_resolve_secret_missing_in_chain_returns_none(tmp_vault):
    set_parent(tmp_vault, "staging", "production")
    assert resolve_secret(tmp_vault, "staging", "MISSING", PASSWORD) is None


def test_resolve_secret_detects_cycle(tmp_vault):
    from envault.inherit import _load_inherit, _save_inherit
    # Manually create a cycle without going through set_parent validation
    _save_inherit(tmp_vault, {"a": "b", "b": "a"})
    with pytest.raises(RuntimeError, match="cycle"):
        resolve_secret(tmp_vault, "a", "KEY", PASSWORD)


# ---------------------------------------------------------------------------
# list_resolved_keys
# ---------------------------------------------------------------------------

def test_list_resolved_keys_includes_parent_keys(tmp_vault):
    _seed(tmp_vault, "production", "SHARED", "val")
    _seed(tmp_vault, "staging", "LOCAL", "val")
    set_parent(tmp_vault, "staging", "production")
    keys = list_resolved_keys(tmp_vault, "staging", PASSWORD)
    assert "SHARED" in keys
    assert "LOCAL" in keys


def test_list_resolved_keys_no_duplicates(tmp_vault):
    _seed(tmp_vault, "production", "KEY", "v1")
    _seed(tmp_vault, "staging", "KEY", "v2")
    set_parent(tmp_vault, "staging", "production")
    keys = list_resolved_keys(tmp_vault, "staging", PASSWORD)
    assert keys.count("KEY") == 1


def test_list_resolved_keys_no_parent(tmp_vault):
    _seed(tmp_vault, "staging", "ONLY", "val")
    keys = list_resolved_keys(tmp_vault, "staging", PASSWORD)
    assert keys == ["ONLY"]
