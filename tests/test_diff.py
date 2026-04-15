"""Tests for envault.diff module."""

import os
import pytest
from envault.vault import set_secret
from envault.diff import diff_envs, format_diff


PASSWORD = "test-password"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_diff_added_keys(tmp_vault):
    set_secret(tmp_vault, "prod", "NEW_KEY", "new_val", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    assert len(result["added"]) == 1
    assert result["added"][0] == ("NEW_KEY", None, "new_val")
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_removed_keys(tmp_vault):
    set_secret(tmp_vault, "staging", "OLD_KEY", "old_val", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    assert len(result["removed"]) == 1
    assert result["removed"][0] == ("OLD_KEY", "old_val", None)
    assert result["added"] == []
    assert result["changed"] == []


def test_diff_changed_keys(tmp_vault):
    set_secret(tmp_vault, "staging", "DB_URL", "postgres://staging", PASSWORD)
    set_secret(tmp_vault, "prod", "DB_URL", "postgres://prod", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    assert len(result["changed"]) == 1
    key, val_a, val_b = result["changed"][0]
    assert key == "DB_URL"
    assert val_a == "postgres://staging"
    assert val_b == "postgres://prod"


def test_diff_no_differences(tmp_vault):
    set_secret(tmp_vault, "staging", "API_KEY", "abc123", PASSWORD)
    set_secret(tmp_vault, "prod", "API_KEY", "abc123", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_both_empty(tmp_vault):
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    assert result == {"added": [], "removed": [], "changed": []}


def test_format_diff_hides_values_by_default(tmp_vault):
    set_secret(tmp_vault, "staging", "SECRET", "s_val", PASSWORD)
    set_secret(tmp_vault, "prod", "SECRET", "p_val", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    output = format_diff(result, "staging", "prod", show_values=False)
    assert "***" in output
    assert "s_val" not in output
    assert "p_val" not in output


def test_format_diff_shows_values_when_requested(tmp_vault):
    set_secret(tmp_vault, "staging", "SECRET", "s_val", PASSWORD)
    set_secret(tmp_vault, "prod", "SECRET", "p_val", PASSWORD)
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    output = format_diff(result, "staging", "prod", show_values=True)
    assert "s_val" in output
    assert "p_val" in output


def test_format_diff_no_differences_message(tmp_vault):
    result = diff_envs(tmp_vault, "staging", "prod", PASSWORD)
    output = format_diff(result, "staging", "prod")
    assert "no differences" in output
