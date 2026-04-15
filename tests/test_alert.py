"""Tests for envault.alert."""

from __future__ import annotations

import datetime
import os
import pytest

from envault.vault import set_secret
from envault.policy import set_policy
from envault.rotation import rotate_secret, record_rotation
from envault import alert


PASSWORD = "test-password"
ENV = "production"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _set(tmp_vault, key, value):
    set_secret(tmp_vault, PASSWORD, ENV, key, value)


# ---------------------------------------------------------------------------
# check_secret
# ---------------------------------------------------------------------------

def test_no_policy_returns_none(tmp_vault):
    _set(tmp_vault, "API_KEY", "abc123")
    assert alert.check_secret(tmp_vault, PASSWORD, ENV, "API_KEY") is None


def test_never_rotated_returns_warning(tmp_vault):
    _set(tmp_vault, "DB_PASS", "secret")
    set_policy(tmp_vault, ENV, "DB_PASS", max_age_days=30)
    result = alert.check_secret(tmp_vault, PASSWORD, ENV, "DB_PASS")
    assert result is not None
    assert result["status"] == "never_rotated"
    assert result["key"] == "DB_PASS"
    assert result["days_since_rotation"] is None


def test_fresh_secret_returns_none(tmp_vault):
    _set(tmp_vault, "TOKEN", "tok")
    set_policy(tmp_vault, ENV, "TOKEN", max_age_days=90)
    # Record a rotation right now
    record_rotation(tmp_vault, PASSWORD, ENV, "TOKEN", "tok")
    result = alert.check_secret(tmp_vault, PASSWORD, ENV, "TOKEN")
    assert result is None


def test_expired_secret_returns_warning(tmp_vault, monkeypatch):
    _set(tmp_vault, "OLD_KEY", "val")
    set_policy(tmp_vault, ENV, "OLD_KEY", max_age_days=1)
    record_rotation(tmp_vault, PASSWORD, ENV, "OLD_KEY", "val")

    # Fake _days_since to return a large number
    monkeypatch.setattr(alert, "_days_since", lambda _ts: 10.0)

    result = alert.check_secret(tmp_vault, PASSWORD, ENV, "OLD_KEY")
    assert result is not None
    assert result["status"] == "expired"
    assert result["days_since_rotation"] == 10.0
    assert "10.0 days" in result["message"]


# ---------------------------------------------------------------------------
# check_all
# ---------------------------------------------------------------------------

def test_check_all_empty_policies(tmp_vault):
    _set(tmp_vault, "X", "1")
    warnings = alert.check_all(tmp_vault, PASSWORD, ENV)
    assert warnings == []


def test_check_all_returns_multiple_warnings(tmp_vault, monkeypatch):
    for key in ("A", "B", "C"):
        _set(tmp_vault, key, "value")
        set_policy(tmp_vault, ENV, key, max_age_days=30)

    # "B" is fresh
    record_rotation(tmp_vault, PASSWORD, ENV, "B", "value")

    warnings = alert.check_all(tmp_vault, PASSWORD, ENV)
    stale_keys = {w["key"] for w in warnings}
    assert "A" in stale_keys
    assert "C" in stale_keys
    assert "B" not in stale_keys
