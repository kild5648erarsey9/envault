"""Tests for envault.ttl."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.ttl import (
    set_ttl,
    get_ttl,
    delete_ttl,
    is_expired,
    check_ttl,
)


@pytest.fixture()
def tmp_vault(tmp_path: Path) -> str:
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def test_set_ttl_returns_iso_string(tmp_vault):
    result = set_ttl(tmp_vault, "production", "API_KEY", 3600)
    assert isinstance(result, str)
    assert "+" in result or "Z" in result or result.endswith("+00:00")


def test_get_ttl_after_set(tmp_vault):
    set_ttl(tmp_vault, "production", "API_KEY", 3600)
    raw = get_ttl(tmp_vault, "production", "API_KEY")
    assert raw is not None
    assert "API_KEY" not in raw  # it's a timestamp, not the key name


def test_get_ttl_missing_returns_none(tmp_vault):
    assert get_ttl(tmp_vault, "production", "MISSING") is None


def test_set_ttl_invalid_seconds_raises(tmp_vault):
    with pytest.raises(ValueError, match="positive"):
        set_ttl(tmp_vault, "production", "API_KEY", -1)


def test_is_expired_no_ttl_returns_none(tmp_vault):
    assert is_expired(tmp_vault, "production", "NO_TTL_KEY") is None


def test_is_not_expired_for_future_ttl(tmp_vault):
    set_ttl(tmp_vault, "staging", "DB_PASS", 3600)
    assert is_expired(tmp_vault, "staging", "DB_PASS") is False


def test_is_expired_for_past_ttl(tmp_vault):
    set_ttl(tmp_vault, "staging", "DB_PASS", 1)
    time.sleep(1.1)
    assert is_expired(tmp_vault, "staging", "DB_PASS") is True


def test_delete_ttl_removes_entry(tmp_vault):
    set_ttl(tmp_vault, "production", "TOKEN", 3600)
    removed = delete_ttl(tmp_vault, "production", "TOKEN")
    assert removed is True
    assert get_ttl(tmp_vault, "production", "TOKEN") is None


def test_delete_ttl_nonexistent_returns_false(tmp_vault):
    assert delete_ttl(tmp_vault, "production", "GHOST") is False


def test_check_ttl_no_ttl(tmp_vault):
    result = check_ttl(tmp_vault, "production", "NOPE")
    assert result == {"has_ttl": False, "expired": None, "expires_at": None}


def test_check_ttl_active(tmp_vault):
    set_ttl(tmp_vault, "production", "KEY", 3600)
    result = check_ttl(tmp_vault, "production", "KEY")
    assert result["has_ttl"] is True
    assert result["expired"] is False
    assert result["expires_at"] is not None


def test_multiple_envs_isolated(tmp_vault):
    set_ttl(tmp_vault, "production", "KEY", 3600)
    assert get_ttl(tmp_vault, "staging", "KEY") is None
