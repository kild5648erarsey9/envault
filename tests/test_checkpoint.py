"""Tests for envault.checkpoint."""

from __future__ import annotations

import pytest

from envault.vault import set_secret
from envault.checkpoint import (
    create_checkpoint,
    get_checkpoint,
    delete_checkpoint,
    verify_checkpoint,
)


PASSWORD = "test-password"
ENV = "production"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(vault_path: str, key: str, value: str) -> None:
    set_secret(vault_path, PASSWORD, ENV, key, value)


# ---------------------------------------------------------------------------
# create_checkpoint
# ---------------------------------------------------------------------------

def test_create_checkpoint_returns_record(tmp_vault):
    _seed(tmp_vault, "DB_PASS", "secret123")
    record = create_checkpoint(tmp_vault, PASSWORD, ENV, "DB_PASS")
    assert record["key"] == "DB_PASS"
    assert record["env"] == ENV
    assert record["value"] == "secret123"
    assert record["timestamp"]


def test_create_checkpoint_with_note(tmp_vault):
    _seed(tmp_vault, "API_KEY", "abc")
    record = create_checkpoint(tmp_vault, PASSWORD, ENV, "API_KEY", note="approved")
    assert record["note"] == "approved"


def test_create_checkpoint_missing_key_raises(tmp_vault):
    with pytest.raises(KeyError, match="DB_PASS"):
        create_checkpoint(tmp_vault, PASSWORD, ENV, "DB_PASS")


# ---------------------------------------------------------------------------
# get_checkpoint
# ---------------------------------------------------------------------------

def test_get_checkpoint_returns_none_when_missing(tmp_vault):
    assert get_checkpoint(tmp_vault, ENV, "GHOST") is None


def test_get_checkpoint_after_create(tmp_vault):
    _seed(tmp_vault, "TOKEN", "xyz")
    create_checkpoint(tmp_vault, PASSWORD, ENV, "TOKEN")
    cp = get_checkpoint(tmp_vault, ENV, "TOKEN")
    assert cp is not None
    assert cp["value"] == "xyz"


# ---------------------------------------------------------------------------
# delete_checkpoint
# ---------------------------------------------------------------------------

def test_delete_checkpoint_returns_true_when_existed(tmp_vault):
    _seed(tmp_vault, "SECRET", "val")
    create_checkpoint(tmp_vault, PASSWORD, ENV, "SECRET")
    assert delete_checkpoint(tmp_vault, ENV, "SECRET") is True
    assert get_checkpoint(tmp_vault, ENV, "SECRET") is None


def test_delete_checkpoint_returns_false_when_missing(tmp_vault):
    assert delete_checkpoint(tmp_vault, ENV, "NOPE") is False


# ---------------------------------------------------------------------------
# verify_checkpoint
# ---------------------------------------------------------------------------

def test_verify_checkpoint_match(tmp_vault):
    _seed(tmp_vault, "PW", "unchanged")
    create_checkpoint(tmp_vault, PASSWORD, ENV, "PW")
    result = verify_checkpoint(tmp_vault, PASSWORD, ENV, "PW")
    assert result["match"] is True
    assert result["live_value"] == "unchanged"


def test_verify_checkpoint_drift(tmp_vault):
    _seed(tmp_vault, "PW", "original")
    create_checkpoint(tmp_vault, PASSWORD, ENV, "PW")
    # Rotate the secret after checkpointing
    set_secret(tmp_vault, PASSWORD, ENV, "PW", "rotated")
    result = verify_checkpoint(tmp_vault, PASSWORD, ENV, "PW")
    assert result["match"] is False
    assert result["live_value"] == "rotated"
    assert result["checkpoint"]["value"] == "original"


def test_verify_checkpoint_no_checkpoint_raises(tmp_vault):
    _seed(tmp_vault, "PW", "val")
    with pytest.raises(KeyError, match="PW"):
        verify_checkpoint(tmp_vault, PASSWORD, ENV, "PW")
