"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path
from envault.audit import record_event, get_events, clear_log, _get_audit_path


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def test_record_event_creates_audit_file(tmp_vault):
    record_event(tmp_vault, "set", "API_KEY", "production")
    audit_path = _get_audit_path(tmp_vault)
    assert audit_path.exists()


def test_record_event_returns_event_dict(tmp_vault):
    event = record_event(tmp_vault, "get", "DB_PASS", "staging")
    assert event["action"] == "get"
    assert event["key"] == "DB_PASS"
    assert event["env"] == "staging"
    assert "timestamp" in event
    assert "user" in event


def test_multiple_events_are_appended(tmp_vault):
    record_event(tmp_vault, "set", "KEY1", "dev")
    record_event(tmp_vault, "get", "KEY1", "dev")
    record_event(tmp_vault, "delete", "KEY1", "dev")
    events = get_events(tmp_vault)
    assert len(events) == 3


def test_get_events_filter_by_key(tmp_vault):
    record_event(tmp_vault, "set", "API_KEY", "dev")
    record_event(tmp_vault, "set", "DB_PASS", "dev")
    events = get_events(tmp_vault, key="API_KEY")
    assert len(events) == 1
    assert events[0]["key"] == "API_KEY"


def test_get_events_filter_by_env(tmp_vault):
    record_event(tmp_vault, "set", "KEY", "dev")
    record_event(tmp_vault, "set", "KEY", "production")
    events = get_events(tmp_vault, env="production")
    assert len(events) == 1
    assert events[0]["env"] == "production"


def test_get_events_filter_by_action(tmp_vault):
    record_event(tmp_vault, "set", "KEY", "dev")
    record_event(tmp_vault, "get", "KEY", "dev")
    events = get_events(tmp_vault, action="set")
    assert len(events) == 1
    assert events[0]["action"] == "set"


def test_get_events_empty_log(tmp_vault):
    events = get_events(tmp_vault)
    assert events == []


def test_clear_log(tmp_vault):
    record_event(tmp_vault, "set", "KEY", "dev")
    record_event(tmp_vault, "get", "KEY", "dev")
    clear_log(tmp_vault)
    events = get_events(tmp_vault)
    assert events == []


def test_event_timestamp_is_iso_format(tmp_vault):
    event = record_event(tmp_vault, "set", "KEY", "dev")
    from datetime import datetime
    # Should not raise
    datetime.fromisoformat(event["timestamp"])
