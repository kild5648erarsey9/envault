"""Tests for envault.access module."""

import pytest
from envault.access import (
    set_access,
    get_access,
    revoke_access,
    can_access,
    list_roles,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_access_returns_entry(tmp_vault):
    entry = set_access(tmp_vault, "dev", "staging", ["DB_URL", "API_KEY"], mode="read")
    assert "DB_URL" in entry["read"]
    assert "API_KEY" in entry["read"]


def test_get_access_after_set(tmp_vault):
    set_access(tmp_vault, "ops", "prod", ["SECRET"], mode="write")
    entry = get_access(tmp_vault, "ops", "prod")
    assert entry is not None
    assert "SECRET" in entry["write"]


def test_get_access_missing_role_returns_none(tmp_vault):
    assert get_access(tmp_vault, "ghost", "prod") is None


def test_set_access_invalid_mode_raises(tmp_vault):
    with pytest.raises(ValueError, match="mode must be"):
        set_access(tmp_vault, "dev", "staging", ["KEY"], mode="execute")


def test_can_access_returns_true_for_granted_key(tmp_vault):
    set_access(tmp_vault, "dev", "staging", ["DB_URL"], mode="read")
    assert can_access(tmp_vault, "dev", "staging", "DB_URL", mode="read") is True


def test_can_access_returns_false_for_missing_key(tmp_vault):
    set_access(tmp_vault, "dev", "staging", ["DB_URL"], mode="read")
    assert can_access(tmp_vault, "dev", "staging", "API_KEY", mode="read") is False


def test_can_access_wildcard(tmp_vault):
    set_access(tmp_vault, "admin", "prod", ["*"], mode="write")
    assert can_access(tmp_vault, "admin", "prod", "ANY_KEY", mode="write") is True


def test_can_access_no_role_returns_false(tmp_vault):
    assert can_access(tmp_vault, "nobody", "prod", "DB_URL") is False


def test_revoke_access_removes_key(tmp_vault):
    set_access(tmp_vault, "dev", "staging", ["DB_URL", "API_KEY"], mode="read")
    entry = revoke_access(tmp_vault, "dev", "staging", ["DB_URL"], mode="read")
    assert "DB_URL" not in entry["read"]
    assert "API_KEY" in entry["read"]


def test_revoke_access_invalid_mode_raises(tmp_vault):
    with pytest.raises(ValueError, match="mode must be"):
        revoke_access(tmp_vault, "dev", "staging", ["KEY"], mode="delete")


def test_revoke_access_nonexistent_key_is_noop(tmp_vault):
    """Revoking a key that was never granted should not raise and leave entry intact."""
    set_access(tmp_vault, "dev", "staging", ["API_KEY"], mode="read")
    entry = revoke_access(tmp_vault, "dev", "staging", ["DB_URL"], mode="read")
    assert "API_KEY" in entry["read"]


def test_list_roles_empty(tmp_vault):
    assert list_roles(tmp_vault) == []


def test_list_roles_after_set(tmp_vault):
    set_access(tmp_vault, "dev", "staging", ["KEY"])
    set_access(tmp_vault, "ops", "prod", ["KEY"])
    roles = list_roles(tmp_vault)
    assert "dev" in roles
    assert "ops" in roles


def test_set_access_accumulates_keys(tmp_vault):
    set_access(tmp_vault, "dev", "staging", ["A"], mode="read")
    set_access(tmp_vault, "dev", "staging", ["B"], mode="read")
    entry = get_access(tmp_vault, "dev", "staging")
    assert "A" in entry["read"]
    assert "B" in entry["read"]
