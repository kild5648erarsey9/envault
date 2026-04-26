"""Tests for envault.merge."""

from __future__ import annotations

import pytest

from envault.vault import set_secret, get_secret
from envault.merge import MergeError, merge_envs, format_merge_report


PASSWORD = "test-password"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _seed(vault_path, env, secrets):
    for k, v in secrets.items():
        set_secret(vault_path, PASSWORD, env, k, v)


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_copies_all_keys(tmp_vault):
    _seed(tmp_vault, "staging", {"DB_URL": "postgres://stg", "API_KEY": "stg-key"})
    written = merge_envs("staging", "production", tmp_vault, PASSWORD)
    assert written == {"DB_URL": "postgres://stg", "API_KEY": "stg-key"}
    assert get_secret(tmp_vault, PASSWORD, "production", "DB_URL") == "postgres://stg"


def test_merge_skips_existing_by_default(tmp_vault):
    _seed(tmp_vault, "staging", {"DB_URL": "postgres://stg", "API_KEY": "stg-key"})
    _seed(tmp_vault, "production", {"DB_URL": "postgres://prod"})
    written = merge_envs("staging", "production", tmp_vault, PASSWORD)
    # DB_URL already in dst — should NOT be overwritten
    assert "DB_URL" not in written
    assert get_secret(tmp_vault, PASSWORD, "production", "DB_URL") == "postgres://prod"
    # API_KEY was missing — should be written
    assert "API_KEY" in written


def test_merge_overwrite_replaces_existing(tmp_vault):
    _seed(tmp_vault, "staging", {"DB_URL": "postgres://stg"})
    _seed(tmp_vault, "production", {"DB_URL": "postgres://prod"})
    written = merge_envs("staging", "production", tmp_vault, PASSWORD, overwrite=True)
    assert "DB_URL" in written
    assert get_secret(tmp_vault, PASSWORD, "production", "DB_URL") == "postgres://stg"


def test_merge_empty_source_raises(tmp_vault):
    with pytest.raises(MergeError, match="no secrets"):
        merge_envs("empty_env", "production", tmp_vault, PASSWORD)


def test_merge_explicit_keys(tmp_vault):
    _seed(tmp_vault, "staging", {"DB_URL": "postgres://stg", "API_KEY": "stg-key", "SECRET": "s"})
    written = merge_envs("staging", "production", tmp_vault, PASSWORD, keys=["API_KEY"])
    assert list(written.keys()) == ["API_KEY"]
    assert get_secret(tmp_vault, PASSWORD, "production", "DB_URL") is None


def test_merge_explicit_keys_missing_raises(tmp_vault):
    _seed(tmp_vault, "staging", {"DB_URL": "postgres://stg"})
    with pytest.raises(MergeError, match="GHOST"):
        merge_envs("staging", "production", tmp_vault, PASSWORD, keys=["GHOST"])


# ---------------------------------------------------------------------------
# format_merge_report
# ---------------------------------------------------------------------------

def test_format_merge_report_with_writes():
    report = format_merge_report({"API_KEY": "x", "DB_URL": "y"}, "production")
    assert "2 secret(s)" in report
    assert "production" in report
    assert "API_KEY" in report
    assert "DB_URL" in report


def test_format_merge_report_empty():
    report = format_merge_report({}, "production")
    assert "No secrets" in report
    assert "production" in report
