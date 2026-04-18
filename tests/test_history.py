"""Tests for envault.history."""
import pytest
from envault.history import (
    record_history,
    get_history,
    clear_history,
    list_history_keys,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_record_history_returns_entry(tmp_vault):
    entry = record_history(tmp_vault, "prod", "DB_PASS", "secret1")
    assert entry["value"] == "secret1"
    assert "recorded_at" in entry


def test_get_history_after_record(tmp_vault):
    record_history(tmp_vault, "prod", "DB_PASS", "v1")
    record_history(tmp_vault, "prod", "DB_PASS", "v2")
    entries = get_history(tmp_vault, "prod", "DB_PASS")
    assert len(entries) == 2
    assert entries[0]["value"] == "v1"
    assert entries[1]["value"] == "v2"


def test_get_history_missing_key_returns_empty(tmp_vault):
    result = get_history(tmp_vault, "prod", "NONEXISTENT")
    assert result == []


def test_get_history_limit(tmp_vault):
    for i in range(10):
        record_history(tmp_vault, "prod", "KEY", f"val{i}")
    entries = get_history(tmp_vault, "prod", "KEY", limit=3)
    assert len(entries) == 3
    assert entries[-1]["value"] == "val9"


def test_clear_history_returns_count(tmp_vault):
    record_history(tmp_vault, "prod", "API_KEY", "a")
    record_history(tmp_vault, "prod", "API_KEY", "b")
    removed = clear_history(tmp_vault, "prod", "API_KEY")
    assert removed == 2
    assert get_history(tmp_vault, "prod", "API_KEY") == []


def test_clear_history_nonexistent_key(tmp_vault):
    assert clear_history(tmp_vault, "prod", "GHOST") == 0


def test_list_history_keys(tmp_vault):
    record_history(tmp_vault, "prod", "A", "1")
    record_history(tmp_vault, "prod", "B", "2")
    keys = list_history_keys(tmp_vault, "prod")
    assert set(keys) == {"A", "B"}


def test_history_isolated_by_env(tmp_vault):
    record_history(tmp_vault, "prod", "X", "prod-val")
    record_history(tmp_vault, "staging", "X", "staging-val")
    prod = get_history(tmp_vault, "prod", "X")
    staging = get_history(tmp_vault, "staging", "X")
    assert prod[0]["value"] == "prod-val"
    assert staging[0]["value"] == "staging-val"
