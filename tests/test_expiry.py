"""Tests for envault.expiry."""

from __future__ import annotations

import time
import pytest

from envault.expiry import (
    set_expiry,
    get_expiry,
    delete_expiry,
    is_expired,
    list_expiring,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault")


ENV = "production"


def test_set_expiry_returns_iso_string(tmp_vault):
    iso = set_expiry(tmp_vault, ENV, "DB_PASS", 3600)
    assert isinstance(iso, str)
    assert "T" in iso  # ISO-8601 format


def test_get_expiry_after_set(tmp_vault):
    iso = set_expiry(tmp_vault, ENV, "API_KEY", 7200)
    assert get_expiry(tmp_vault, ENV, "API_KEY") == iso


def test_get_expiry_missing_returns_none(tmp_vault):
    assert get_expiry(tmp_vault, ENV, "NONEXISTENT") is None


def test_set_expiry_invalid_seconds_raises(tmp_vault):
    with pytest.raises(ValueError, match="positive"):
        set_expiry(tmp_vault, ENV, "KEY", 0)
    with pytest.raises(ValueError, match="positive"):
        set_expiry(tmp_vault, ENV, "KEY", -10)


def test_is_expired_not_yet(tmp_vault):
    set_expiry(tmp_vault, ENV, "TOKEN", 9999)
    assert is_expired(tmp_vault, ENV, "TOKEN") is False


def test_is_expired_past(tmp_vault):
    # Set expiry 1 second in the future then sleep just past it
    set_expiry(tmp_vault, ENV, "SHORT", 1)
    time.sleep(1.1)
    assert is_expired(tmp_vault, ENV, "SHORT") is True


def test_is_expired_no_expiry_returns_none(tmp_vault):
    assert is_expired(tmp_vault, ENV, "NO_EXPIRY") is None


def test_delete_expiry_removes_entry(tmp_vault):
    set_expiry(tmp_vault, ENV, "TEMP", 3600)
    assert delete_expiry(tmp_vault, ENV, "TEMP") is True
    assert get_expiry(tmp_vault, ENV, "TEMP") is None


def test_delete_expiry_absent_returns_false(tmp_vault):
    assert delete_expiry(tmp_vault, ENV, "GHOST") is False


def test_list_expiring_sorted(tmp_vault):
    set_expiry(tmp_vault, ENV, "SLOW", 7200)
    set_expiry(tmp_vault, ENV, "FAST", 60)
    items = list_expiring(tmp_vault, ENV)
    assert len(items) == 2
    assert items[0]["key"] == "FAST"  # expires sooner → first
    assert items[1]["key"] == "SLOW"


def test_list_expiring_empty(tmp_vault):
    assert list_expiring(tmp_vault, "staging") == []


def test_list_expiring_expired_flag(tmp_vault):
    set_expiry(tmp_vault, ENV, "LIVE", 9999)
    items = list_expiring(tmp_vault, ENV)
    assert items[0]["expired"] is False
