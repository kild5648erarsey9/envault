"""Tests for envault.group."""

from __future__ import annotations

import pytest

from envault.group import (
    add_to_group,
    delete_group,
    find_groups_for_key,
    get_group,
    list_groups,
    remove_from_group,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.enc"
    vault_file.write_text("{}")  # minimal placeholder
    return str(vault_file)


# ---------------------------------------------------------------------------
# add_to_group
# ---------------------------------------------------------------------------

def test_add_to_group_returns_sorted_members(tmp_vault):
    members = add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert members == ["DB_HOST"]


def test_add_multiple_keys_sorted(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_PORT")
    members = add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert members == ["DB_HOST", "DB_PORT"]


def test_add_duplicate_key_is_idempotent(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    members = add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert members.count("DB_HOST") == 1


def test_add_to_group_empty_name_raises(tmp_vault):
    with pytest.raises(ValueError, match="empty"):
        add_to_group(tmp_vault, "prod", "  ", "DB_HOST")


# ---------------------------------------------------------------------------
# get_group
# ---------------------------------------------------------------------------

def test_get_group_after_add(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert get_group(tmp_vault, "prod", "infra") == ["DB_HOST"]


def test_get_group_missing_returns_none(tmp_vault):
    assert get_group(tmp_vault, "prod", "nonexistent") is None


# ---------------------------------------------------------------------------
# remove_from_group
# ---------------------------------------------------------------------------

def test_remove_from_group(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    add_to_group(tmp_vault, "prod", "infra", "DB_PORT")
    members = remove_from_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert "DB_HOST" not in members
    assert "DB_PORT" in members


def test_remove_nonexistent_key_is_safe(tmp_vault):
    members = remove_from_group(tmp_vault, "prod", "infra", "MISSING_KEY")
    assert members == []


# ---------------------------------------------------------------------------
# list_groups
# ---------------------------------------------------------------------------

def test_list_groups_empty(tmp_vault):
    assert list_groups(tmp_vault, "prod") == []


def test_list_groups_returns_sorted(tmp_vault):
    add_to_group(tmp_vault, "prod", "workers", "WORKER_KEY")
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert list_groups(tmp_vault, "prod") == ["infra", "workers"]


# ---------------------------------------------------------------------------
# delete_group
# ---------------------------------------------------------------------------

def test_delete_group_returns_true(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert delete_group(tmp_vault, "prod", "infra") is True
    assert get_group(tmp_vault, "prod", "infra") is None


def test_delete_missing_group_returns_false(tmp_vault):
    assert delete_group(tmp_vault, "prod", "ghost") is False


# ---------------------------------------------------------------------------
# find_groups_for_key
# ---------------------------------------------------------------------------

def test_find_groups_for_key(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    add_to_group(tmp_vault, "prod", "monitoring", "DB_HOST")
    groups = find_groups_for_key(tmp_vault, "prod", "DB_HOST")
    assert groups == ["infra", "monitoring"]


def test_find_groups_for_key_not_member(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert find_groups_for_key(tmp_vault, "prod", "API_KEY") == []


def test_groups_are_isolated_by_env(tmp_vault):
    add_to_group(tmp_vault, "prod", "infra", "DB_HOST")
    assert get_group(tmp_vault, "staging", "infra") is None
