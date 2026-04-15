"""Tests for envault.compare."""

from __future__ import annotations

import pytest

from envault.vault import set_secret
from envault.compare import compare_envs, format_compare

PASSWORD = "test-password"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _seed(vault_path: str) -> None:
    """Populate two environments with a mix of shared and unique keys."""
    # staging
    set_secret(vault_path, PASSWORD, "staging", "DB_HOST", "staging.db.local")
    set_secret(vault_path, PASSWORD, "staging", "DB_PASS", "s3cr3t")
    set_secret(vault_path, PASSWORD, "staging", "ONLY_STAGING", "yes")
    # production
    set_secret(vault_path, PASSWORD, "production", "DB_HOST", "prod.db.local")
    set_secret(vault_path, PASSWORD, "production", "DB_PASS", "s3cr3t")
    set_secret(vault_path, PASSWORD, "production", "ONLY_PROD", "yes")


def test_compare_match_key(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    db_pass = next(r for r in results if r.key == "DB_PASS")
    assert db_pass.match is True


def test_compare_differ_key(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    db_host = next(r for r in results if r.key == "DB_HOST")
    assert db_host.match is False
    assert db_host.value_a == "staging.db.local"
    assert db_host.value_b == "prod.db.local"


def test_compare_missing_in_one_env(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    only_staging = next(r for r in results if r.key == "ONLY_STAGING")
    assert only_staging.match is False
    assert only_staging.value_a == "yes"
    assert only_staging.value_b is None


def test_compare_results_sorted(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    keys = [r.key for r in results]
    assert keys == sorted(keys)


def test_compare_explicit_keys(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(
        tmp_vault, PASSWORD, "staging", "production", keys=["DB_HOST"]
    )
    assert len(results) == 1
    assert results[0].key == "DB_HOST"


def test_compare_empty_envs(tmp_vault):
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    assert results == []


def test_format_compare_no_results(tmp_vault):
    output = format_compare([])
    assert "No keys" in output


def test_format_compare_hides_values_by_default(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    output = format_compare(results)
    assert "staging.db.local" not in output
    assert "***" in output


def test_format_compare_reveals_values(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    output = format_compare(results, reveal=True)
    assert "staging.db.local" in output
    assert "prod.db.local" in output


def test_format_compare_shows_missing_label(tmp_vault):
    _seed(tmp_vault)
    results = compare_envs(tmp_vault, PASSWORD, "staging", "production")
    output = format_compare(results, reveal=True)
    assert "<missing>" in output
