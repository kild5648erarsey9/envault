"""Tests for envault.watermark."""

from __future__ import annotations

import pytest

from envault.watermark import (
    delete_watermark,
    get_watermark,
    list_watermarks,
    set_watermark,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_set_watermark_returns_mark(tmp_vault):
    result = set_watermark(tmp_vault, "prod", "DB_PASS", "owner:alice")
    assert result == "owner:alice"


def test_get_watermark_after_set(tmp_vault):
    set_watermark(tmp_vault, "prod", "DB_PASS", "team:backend")
    assert get_watermark(tmp_vault, "prod", "DB_PASS") == "team:backend"


def test_get_watermark_missing_returns_none(tmp_vault):
    assert get_watermark(tmp_vault, "prod", "MISSING") is None


def test_get_watermark_wrong_env_returns_none(tmp_vault):
    set_watermark(tmp_vault, "prod", "API_KEY", "v1")
    assert get_watermark(tmp_vault, "staging", "API_KEY") is None


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def test_set_watermark_empty_raises(tmp_vault):
    with pytest.raises(ValueError, match="empty"):
        set_watermark(tmp_vault, "prod", "KEY", "")


def test_set_watermark_blank_raises(tmp_vault):
    with pytest.raises(ValueError, match="empty"):
        set_watermark(tmp_vault, "prod", "KEY", "   ")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_watermark_returns_true(tmp_vault):
    set_watermark(tmp_vault, "prod", "DB_PASS", "sensitive")
    assert delete_watermark(tmp_vault, "prod", "DB_PASS") is True


def test_delete_watermark_removes_entry(tmp_vault):
    set_watermark(tmp_vault, "prod", "DB_PASS", "sensitive")
    delete_watermark(tmp_vault, "prod", "DB_PASS")
    assert get_watermark(tmp_vault, "prod", "DB_PASS") is None


def test_delete_nonexistent_returns_false(tmp_vault):
    assert delete_watermark(tmp_vault, "prod", "GHOST") is False


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_watermarks_returns_dict(tmp_vault):
    set_watermark(tmp_vault, "prod", "A", "mark-a")
    set_watermark(tmp_vault, "prod", "B", "mark-b")
    result = list_watermarks(tmp_vault, "prod")
    assert result == {"A": "mark-a", "B": "mark-b"}


def test_list_watermarks_empty_env(tmp_vault):
    assert list_watermarks(tmp_vault, "empty") == {}


def test_list_watermarks_isolated_by_env(tmp_vault):
    set_watermark(tmp_vault, "prod", "X", "px")
    set_watermark(tmp_vault, "staging", "Y", "sy")
    assert list_watermarks(tmp_vault, "prod") == {"X": "px"}
    assert list_watermarks(tmp_vault, "staging") == {"Y": "sy"}
