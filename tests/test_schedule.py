"""Tests for envault.schedule."""
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from envault.schedule import (
    set_schedule, get_schedule, remove_schedule, list_schedules, due_for_rotation
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_schedule_returns_entry(tmp_vault):
    entry = set_schedule(tmp_vault, "prod", "DB_PASS", "monthly")
    assert entry["interval"] == "monthly"
    assert entry["interval_days"] == 30
    assert "created_at" in entry


def test_get_schedule_after_set(tmp_vault):
    set_schedule(tmp_vault, "prod", "DB_PASS", "weekly")
    entry = get_schedule(tmp_vault, "prod", "DB_PASS")
    assert entry is not None
    assert entry["interval"] == "weekly"


def test_get_schedule_missing_returns_none(tmp_vault):
    assert get_schedule(tmp_vault, "prod", "MISSING") is None


def test_set_schedule_invalid_interval_raises(tmp_vault):
    with pytest.raises(ValueError, match="Invalid interval"):
        set_schedule(tmp_vault, "prod", "KEY", "hourly")


def test_remove_schedule_returns_true(tmp_vault):
    set_schedule(tmp_vault, "prod", "API_KEY", "quarterly")
    assert remove_schedule(tmp_vault, "prod", "API_KEY") is True
    assert get_schedule(tmp_vault, "prod", "API_KEY") is None


def test_remove_nonexistent_returns_false(tmp_vault):
    assert remove_schedule(tmp_vault, "prod", "GHOST") is False


def test_list_schedules(tmp_vault):
    set_schedule(tmp_vault, "staging", "KEY_A", "daily")
    set_schedule(tmp_vault, "staging", "KEY_B", "yearly")
    result = list_schedules(tmp_vault, "staging")
    assert set(result.keys()) == {"KEY_A", "KEY_B"}


def test_list_schedules_empty_env(tmp_vault):
    assert list_schedules(tmp_vault, "empty") == {}


def test_due_for_rotation_no_schedule(tmp_vault):
    assert due_for_rotation(tmp_vault, "prod", "KEY", None) is False


def test_due_for_rotation_never_rotated(tmp_vault):
    set_schedule(tmp_vault, "prod", "KEY", "weekly")
    assert due_for_rotation(tmp_vault, "prod", "KEY", None) is True


def test_due_for_rotation_fresh(tmp_vault):
    set_schedule(tmp_vault, "prod", "KEY", "monthly")
    recent = datetime.now(timezone.utc).isoformat()
    assert due_for_rotation(tmp_vault, "prod", "KEY", recent) is False


def test_due_for_rotation_stale(tmp_vault):
    set_schedule(tmp_vault, "prod", "KEY", "weekly")
    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    assert due_for_rotation(tmp_vault, "prod", "KEY", old) is True
