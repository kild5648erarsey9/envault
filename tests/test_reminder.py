"""Tests for envault.reminder module."""

import pytest
from pathlib import Path

from envault.reminder import (
    set_reminder,
    get_reminder,
    delete_reminder,
    list_reminders,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_reminder_returns_entry(tmp_vault):
    entry = set_reminder(tmp_vault, "prod", "DB_PASS", "Rotate every 90 days")
    assert entry["note"] == "Rotate every 90 days"
    assert "created_at" in entry


def test_get_reminder_after_set(tmp_vault):
    set_reminder(tmp_vault, "prod", "API_KEY", "Check vendor portal")
    result = get_reminder(tmp_vault, "prod", "API_KEY")
    assert result is not None
    assert result["note"] == "Check vendor portal"


def test_get_reminder_missing_returns_none(tmp_vault):
    assert get_reminder(tmp_vault, "prod", "NONEXISTENT") is None


def test_set_reminder_empty_note_raises(tmp_vault):
    with pytest.raises(ValueError, match="empty"):
        set_reminder(tmp_vault, "prod", "KEY", "   ")


def test_delete_reminder_returns_true_when_exists(tmp_vault):
    set_reminder(tmp_vault, "prod", "SECRET", "A note")
    assert delete_reminder(tmp_vault, "prod", "SECRET") is True


def test_delete_reminder_returns_false_when_missing(tmp_vault):
    assert delete_reminder(tmp_vault, "prod", "GHOST") is False


def test_delete_reminder_removes_entry(tmp_vault):
    set_reminder(tmp_vault, "prod", "TOKEN", "Temp token")
    delete_reminder(tmp_vault, "prod", "TOKEN")
    assert get_reminder(tmp_vault, "prod", "TOKEN") is None


def test_list_reminders_empty(tmp_vault):
    assert list_reminders(tmp_vault, "staging") == {}


def test_list_reminders_multiple(tmp_vault):
    set_reminder(tmp_vault, "prod", "A", "Note A")
    set_reminder(tmp_vault, "prod", "B", "Note B")
    result = list_reminders(tmp_vault, "prod")
    assert set(result.keys()) == {"A", "B"}


def test_reminder_file_created(tmp_vault):
    set_reminder(tmp_vault, "dev", "KEY", "Important")
    reminder_file = Path(tmp_vault) / "dev" / ".reminders.json"
    assert reminder_file.exists()


def test_set_reminder_overwrites_existing(tmp_vault):
    set_reminder(tmp_vault, "prod", "KEY", "Old note")
    set_reminder(tmp_vault, "prod", "KEY", "New note")
    result = get_reminder(tmp_vault, "prod", "KEY")
    assert result["note"] == "New note"
