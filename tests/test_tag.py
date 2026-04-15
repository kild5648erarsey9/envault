"""Tests for envault.tag module."""

import pytest

from envault.tag import add_tag, remove_tag, get_tags, list_by_tag, clear_tags


@pytest.fixture()
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def test_add_tag_returns_list(tmp_vault):
    tags = add_tag(tmp_vault, "prod", "DB_URL", "database")
    assert tags == ["database"]


def test_add_tag_multiple(tmp_vault):
    add_tag(tmp_vault, "prod", "DB_URL", "database")
    tags = add_tag(tmp_vault, "prod", "DB_URL", "critical")
    assert "database" in tags
    assert "critical" in tags


def test_add_tag_duplicate_ignored(tmp_vault):
    add_tag(tmp_vault, "prod", "DB_URL", "database")
    tags = add_tag(tmp_vault, "prod", "DB_URL", "database")
    assert tags.count("database") == 1


def test_get_tags_empty(tmp_vault):
    assert get_tags(tmp_vault, "prod", "MISSING_KEY") == []


def test_get_tags_after_add(tmp_vault):
    add_tag(tmp_vault, "staging", "API_KEY", "auth")
    assert get_tags(tmp_vault, "staging", "API_KEY") == ["auth"]


def test_remove_tag(tmp_vault):
    add_tag(tmp_vault, "prod", "SECRET", "sensitive")
    add_tag(tmp_vault, "prod", "SECRET", "auth")
    remaining = remove_tag(tmp_vault, "prod", "SECRET", "sensitive")
    assert "sensitive" not in remaining
    assert "auth" in remaining


def test_remove_last_tag_cleans_key(tmp_vault):
    add_tag(tmp_vault, "prod", "SOLO", "only")
    remove_tag(tmp_vault, "prod", "SOLO", "only")
    assert get_tags(tmp_vault, "prod", "SOLO") == []


def test_remove_nonexistent_tag_is_safe(tmp_vault):
    remaining = remove_tag(tmp_vault, "prod", "GHOST", "nope")
    assert remaining == []


def test_list_by_tag(tmp_vault):
    add_tag(tmp_vault, "prod", "DB_URL", "database")
    add_tag(tmp_vault, "prod", "DB_PASS", "database")
    add_tag(tmp_vault, "prod", "API_KEY", "auth")
    keys = list_by_tag(tmp_vault, "prod", "database")
    assert set(keys) == {"DB_URL", "DB_PASS"}


def test_list_by_tag_no_match(tmp_vault):
    assert list_by_tag(tmp_vault, "prod", "nonexistent") == []


def test_clear_tags(tmp_vault):
    add_tag(tmp_vault, "dev", "KEY", "t1")
    add_tag(tmp_vault, "dev", "KEY", "t2")
    clear_tags(tmp_vault, "dev", "KEY")
    assert get_tags(tmp_vault, "dev", "KEY") == []


def test_tags_are_env_scoped(tmp_vault):
    add_tag(tmp_vault, "prod", "KEY", "production-only")
    assert get_tags(tmp_vault, "staging", "KEY") == []
