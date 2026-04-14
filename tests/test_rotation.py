"""Tests for envault.rotation module."""

import json
import pytest

from envault.vault import set_secret
from envault.rotation import (
    rotate_secret,
    get_rotation_info,
    record_rotation,
    list_rotation_info,
)


PASSWORD = "test-password"
ENV = "production"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_rotate_secret_updates_value(tmp_vault):
    set_secret(tmp_vault, ENV, "API_KEY", "old-value", PASSWORD)
    rotate_secret(tmp_vault, ENV, "API_KEY", "new-value", PASSWORD)

    from envault.vault import get_secret
    result = get_secret(tmp_vault, ENV, "API_KEY", PASSWORD)
    assert result == "new-value"


def test_rotate_secret_records_timestamp(tmp_vault):
    set_secret(tmp_vault, ENV, "DB_PASS", "secret", PASSWORD)
    ts = rotate_secret(tmp_vault, ENV, "DB_PASS", "new-secret", PASSWORD)

    info = get_rotation_info(tmp_vault, ENV, "DB_PASS")
    assert info is not None
    assert info["last_rotated"] == ts


def test_rotate_nonexistent_key_raises(tmp_vault):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        rotate_secret(tmp_vault, ENV, "MISSING_KEY", "value", PASSWORD)


def test_record_rotation_returns_iso_string(tmp_vault):
    set_secret(tmp_vault, ENV, "TOKEN", "abc", PASSWORD)
    ts = record_rotation(tmp_vault, ENV, "TOKEN")
    # Basic ISO 8601 sanity check
    assert "T" in ts
    assert "+" in ts or ts.endswith("Z") or "00:00" in ts


def test_get_rotation_info_none_for_untracked(tmp_vault):
    set_secret(tmp_vault, ENV, "UNTRACKED", "val", PASSWORD)
    assert get_rotation_info(tmp_vault, ENV, "UNTRACKED") is None


def test_list_rotation_info_empty(tmp_vault):
    result = list_rotation_info(tmp_vault, ENV)
    assert result == {}


def test_list_rotation_info_multiple_keys(tmp_vault):
    for key in ("KEY_A", "KEY_B", "KEY_C"):
        set_secret(tmp_vault, ENV, key, "value", PASSWORD)
        record_rotation(tmp_vault, ENV, key)

    info = list_rotation_info(tmp_vault, ENV)
    assert set(info.keys()) == {"KEY_A", "KEY_B", "KEY_C"}
    for v in info.values():
        assert "last_rotated" in v
