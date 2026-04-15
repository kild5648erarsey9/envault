"""Tests for envault.lock module."""

import pytest

from envault.lock import (
    lock_secret,
    unlock_secret,
    is_locked,
    list_locked,
    assert_unlocked,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_lock_secret_returns_list(tmp_vault):
    result = lock_secret(tmp_vault, "prod", "API_KEY")
    assert "API_KEY" in result


def test_is_locked_after_lock(tmp_vault):
    lock_secret(tmp_vault, "prod", "DB_PASS")
    assert is_locked(tmp_vault, "prod", "DB_PASS") is True


def test_is_not_locked_by_default(tmp_vault):
    assert is_locked(tmp_vault, "prod", "NONEXISTENT") is False


def test_unlock_secret_removes_lock(tmp_vault):
    lock_secret(tmp_vault, "prod", "TOKEN")
    unlock_secret(tmp_vault, "prod", "TOKEN")
    assert is_locked(tmp_vault, "prod", "TOKEN") is False


def test_unlock_nonexistent_key_is_noop(tmp_vault):
    result = unlock_secret(tmp_vault, "prod", "GHOST")
    assert "GHOST" not in result


def test_lock_duplicate_ignored(tmp_vault):
    lock_secret(tmp_vault, "prod", "API_KEY")
    result = lock_secret(tmp_vault, "prod", "API_KEY")
    assert result.count("API_KEY") == 1


def test_list_locked_returns_all(tmp_vault):
    lock_secret(tmp_vault, "staging", "KEY_A")
    lock_secret(tmp_vault, "staging", "KEY_B")
    locked = list_locked(tmp_vault, "staging")
    assert "KEY_A" in locked
    assert "KEY_B" in locked


def test_list_locked_empty_env(tmp_vault):
    assert list_locked(tmp_vault, "dev") == []


def test_locks_are_env_scoped(tmp_vault):
    lock_secret(tmp_vault, "prod", "SECRET")
    assert is_locked(tmp_vault, "dev", "SECRET") is False


def test_assert_unlocked_raises_when_locked(tmp_vault):
    lock_secret(tmp_vault, "prod", "API_KEY")
    with pytest.raises(ValueError, match="locked"):
        assert_unlocked(tmp_vault, "prod", "API_KEY")


def test_assert_unlocked_passes_when_not_locked(tmp_vault):
    assert_unlocked(tmp_vault, "prod", "FREE_KEY")  # should not raise
