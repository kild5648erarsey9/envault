"""Tests for envault/label.py"""

import pytest
from envault.label import (
    add_label,
    remove_label,
    get_labels,
    find_by_label,
    clear_labels,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_add_label_returns_sorted_list(tmp_vault):
    result = add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    assert result == ["sensitive"]


def test_add_multiple_labels(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    result = add_label(tmp_vault, "prod", "DB_PASS", "database")
    assert result == ["database", "sensitive"]


def test_add_duplicate_label_ignored(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    result = add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    assert result == ["sensitive"]


def test_add_empty_label_raises(tmp_vault):
    with pytest.raises(ValueError, match="empty"):
        add_label(tmp_vault, "prod", "DB_PASS", "   ")


def test_get_labels_empty(tmp_vault):
    assert get_labels(tmp_vault, "prod", "MISSING") == []


def test_get_labels_after_add(tmp_vault):
    add_label(tmp_vault, "staging", "API_KEY", "external")
    add_label(tmp_vault, "staging", "API_KEY", "rotate-monthly")
    labels = get_labels(tmp_vault, "staging", "API_KEY")
    assert "external" in labels
    assert "rotate-monthly" in labels


def test_remove_label(tmp_vault):
    add_label(tmp_vault, "prod", "TOKEN", "critical")
    add_label(tmp_vault, "prod", "TOKEN", "auth")
    result = remove_label(tmp_vault, "prod", "TOKEN", "critical")
    assert "critical" not in result
    assert "auth" in result


def test_remove_nonexistent_label_is_noop(tmp_vault):
    add_label(tmp_vault, "prod", "TOKEN", "auth")
    result = remove_label(tmp_vault, "prod", "TOKEN", "ghost")
    assert result == ["auth"]


def test_find_by_label_returns_matching_keys(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    add_label(tmp_vault, "prod", "API_KEY", "sensitive")
    add_label(tmp_vault, "prod", "LOG_LEVEL", "config")
    keys = find_by_label(tmp_vault, "prod", "sensitive")
    assert set(keys) == {"DB_PASS", "API_KEY"}


def test_find_by_label_restricted_to_env(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    add_label(tmp_vault, "staging", "DB_PASS", "sensitive")
    keys = find_by_label(tmp_vault, "prod", "sensitive")
    assert keys == ["DB_PASS"]


def test_find_by_label_no_match(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    assert find_by_label(tmp_vault, "prod", "nonexistent") == []


def test_clear_labels(tmp_vault):
    add_label(tmp_vault, "prod", "DB_PASS", "sensitive")
    add_label(tmp_vault, "prod", "DB_PASS", "critical")
    clear_labels(tmp_vault, "prod", "DB_PASS")
    assert get_labels(tmp_vault, "prod", "DB_PASS") == []


def test_clear_labels_missing_key_is_noop(tmp_vault):
    clear_labels(tmp_vault, "prod", "NONEXISTENT")  # should not raise
