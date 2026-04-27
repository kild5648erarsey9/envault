"""Tests for envault.quota."""

from __future__ import annotations

import pytest

from envault.quota import (
    check_quota,
    delete_quota,
    get_quota,
    list_quotas,
    set_quota,
)
from envault.vault import set_secret


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_quota(tmp_vault):
    result = set_quota(tmp_vault, "production", 10)
    assert result == 10
    assert get_quota(tmp_vault, "production") == 10


def test_get_quota_missing_returns_none(tmp_vault):
    assert get_quota(tmp_vault, "staging") is None


def test_set_quota_invalid_limit_raises(tmp_vault):
    with pytest.raises(ValueError, match="positive integer"):
        set_quota(tmp_vault, "dev", 0)

    with pytest.raises(ValueError, match="positive integer"):
        set_quota(tmp_vault, "dev", -5)


def test_delete_quota_returns_true(tmp_vault):
    set_quota(tmp_vault, "dev", 5)
    assert delete_quota(tmp_vault, "dev") is True
    assert get_quota(tmp_vault, "dev") is None


def test_delete_quota_missing_returns_false(tmp_vault):
    assert delete_quota(tmp_vault, "nonexistent") is False


def test_list_quotas_empty(tmp_vault):
    assert list_quotas(tmp_vault) == {}


def test_list_quotas_multiple(tmp_vault):
    set_quota(tmp_vault, "dev", 5)
    set_quota(tmp_vault, "staging", 20)
    set_quota(tmp_vault, "production", 50)
    result = list_quotas(tmp_vault)
    assert result == {"dev": 5, "staging": 20, "production": 50}


def test_check_quota_no_policy_returns_none(tmp_vault):
    set_secret(tmp_vault, "dev", "KEY", "val", "pw")
    assert check_quota(tmp_vault, "dev", "pw") is None


def test_check_quota_under_limit_returns_none(tmp_vault):
    set_secret(tmp_vault, "dev", "KEY", "val", "pw")
    set_quota(tmp_vault, "dev", 5)
    assert check_quota(tmp_vault, "dev", "pw") is None


def test_check_quota_at_limit_returns_warning(tmp_vault):
    set_secret(tmp_vault, "dev", "A", "1", "pw")
    set_secret(tmp_vault, "dev", "B", "2", "pw")
    set_quota(tmp_vault, "dev", 2)
    warning = check_quota(tmp_vault, "dev", "pw")
    assert warning is not None
    assert "2/2" in warning
    assert "dev" in warning


def test_check_quota_over_limit_returns_warning(tmp_vault):
    set_secret(tmp_vault, "dev", "A", "1", "pw")
    set_secret(tmp_vault, "dev", "B", "2", "pw")
    set_secret(tmp_vault, "dev", "C", "3", "pw")
    set_quota(tmp_vault, "dev", 2)
    warning = check_quota(tmp_vault, "dev", "pw")
    assert warning is not None
    assert "3/2" in warning
