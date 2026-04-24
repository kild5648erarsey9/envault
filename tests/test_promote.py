"""Tests for envault.promote."""

import os
import pytest

from envault.vault import set_secret, get_secret
from envault.promote import promote_secret, promote_all, PromoteError


PASSWORD = "test-password"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _seed(vault_path, env, **secrets):
    for k, v in secrets.items():
        set_secret(vault_path, PASSWORD, env, k, v)


# ---------------------------------------------------------------------------
# promote_secret
# ---------------------------------------------------------------------------

def test_promote_secret_copies_value(tmp_vault):
    _seed(tmp_vault, "staging", DB_URL="postgres://staging")
    value = promote_secret(tmp_vault, PASSWORD, "DB_URL", "staging", "prod")
    assert value == "postgres://staging"
    assert get_secret(tmp_vault, PASSWORD, "prod", "DB_URL") == "postgres://staging"


def test_promote_secret_missing_key_raises(tmp_vault):
    with pytest.raises(PromoteError, match="not found in environment"):
        promote_secret(tmp_vault, PASSWORD, "MISSING", "staging", "prod")


def test_promote_secret_existing_no_overwrite_raises(tmp_vault):
    _seed(tmp_vault, "staging", API_KEY="abc")
    _seed(tmp_vault, "prod", API_KEY="xyz")
    with pytest.raises(PromoteError, match="already exists"):
        promote_secret(tmp_vault, PASSWORD, "API_KEY", "staging", "prod")


def test_promote_secret_overwrite_replaces_value(tmp_vault):
    _seed(tmp_vault, "staging", API_KEY="new-value")
    _seed(tmp_vault, "prod", API_KEY="old-value")
    promote_secret(
        tmp_vault, PASSWORD, "API_KEY", "staging", "prod", overwrite=True
    )
    assert get_secret(tmp_vault, PASSWORD, "prod", "API_KEY") == "new-value"


def test_promote_secret_does_not_remove_src(tmp_vault):
    _seed(tmp_vault, "staging", TOKEN="tok")
    promote_secret(tmp_vault, PASSWORD, "TOKEN", "staging", "prod")
    assert get_secret(tmp_vault, PASSWORD, "staging", "TOKEN") == "tok"


# ---------------------------------------------------------------------------
# promote_all
# ---------------------------------------------------------------------------

def test_promote_all_copies_all_keys(tmp_vault):
    _seed(tmp_vault, "staging", A="1", B="2", C="3")
    result = promote_all(tmp_vault, PASSWORD, "staging", "prod")
    assert result == {"A": "1", "B": "2", "C": "3"}
    for k, v in result.items():
        assert get_secret(tmp_vault, PASSWORD, "prod", k) == v


def test_promote_all_respects_exclude(tmp_vault):
    _seed(tmp_vault, "staging", A="1", B="2", C="3")
    result = promote_all(tmp_vault, PASSWORD, "staging", "prod", exclude=["B"])
    assert "B" not in result
    assert get_secret(tmp_vault, PASSWORD, "prod", "B") is None


def test_promote_all_empty_env_returns_empty(tmp_vault):
    result = promote_all(tmp_vault, PASSWORD, "staging", "prod")
    assert result == {}


def test_promote_all_overwrite_flag_propagated(tmp_vault):
    _seed(tmp_vault, "staging", X="new")
    _seed(tmp_vault, "prod", X="old")
    result = promote_all(
        tmp_vault, PASSWORD, "staging", "prod", overwrite=True
    )
    assert result["X"] == "new"
