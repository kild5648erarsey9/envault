"""Tests for envault.policy module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.policy import (
    set_policy,
    get_policy,
    delete_policy,
    list_policies,
    check_violations,
)


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("{}")
    return str(vault_file)


def test_set_and_get_policy(tmp_vault):
    result = set_policy(tmp_vault, "prod", "DB_PASSWORD", max_age_days=30)
    assert result["max_age_days"] == 30
    policy = get_policy(tmp_vault, "prod", "DB_PASSWORD")
    assert policy is not None
    assert policy["max_age_days"] == 30


def test_get_policy_missing_key_returns_none(tmp_vault):
    assert get_policy(tmp_vault, "prod", "NONEXISTENT") is None


def test_set_policy_invalid_age_raises(tmp_vault):
    with pytest.raises(ValueError, match="positive integer"):
        set_policy(tmp_vault, "prod", "API_KEY", max_age_days=0)


def test_delete_policy(tmp_vault):
    set_policy(tmp_vault, "prod", "SECRET", max_age_days=60)
    removed = delete_policy(tmp_vault, "prod", "SECRET")
    assert removed is True
    assert get_policy(tmp_vault, "prod", "SECRET") is None


def test_delete_policy_nonexistent_returns_false(tmp_vault):
    assert delete_policy(tmp_vault, "prod", "GHOST") is False


def test_list_policies(tmp_vault):
    set_policy(tmp_vault, "staging", "KEY_A", max_age_days=15)
    set_policy(tmp_vault, "staging", "KEY_B", max_age_days=45)
    policies = list_policies(tmp_vault, "staging")
    assert "KEY_A" in policies
    assert "KEY_B" in policies
    assert policies["KEY_A"]["max_age_days"] == 15


def test_list_policies_empty_env(tmp_vault):
    assert list_policies(tmp_vault, "empty_env") == {}


def test_check_violations_never_rotated(tmp_vault):
    set_policy(tmp_vault, "prod", "UNROTATED_KEY", max_age_days=30)
    with patch("envault.policy.get_rotation_info", return_value=None):
        violations = check_violations(tmp_vault, "prod")
    assert any(v["key"] == "UNROTATED_KEY" and "never rotated" in v["reason"]
               for v in violations)


def test_check_violations_exceeded(tmp_vault):
    from datetime import datetime, timezone, timedelta
    set_policy(tmp_vault, "prod", "OLD_KEY", max_age_days=10)
    old_date = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    with patch("envault.policy.get_rotation_info",
               return_value={"last_rotated": old_date}):
        violations = check_violations(tmp_vault, "prod")
    assert any(v["key"] == "OLD_KEY" for v in violations)


def test_check_violations_within_policy(tmp_vault):
    from datetime import datetime, timezone, timedelta
    set_policy(tmp_vault, "prod", "FRESH_KEY", max_age_days=30)
    recent_date = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    with patch("envault.policy.get_rotation_info",
               return_value={"last_rotated": recent_date}):
        violations = check_violations(tmp_vault, "prod")
    assert not any(v["key"] == "FRESH_KEY" for v in violations)
