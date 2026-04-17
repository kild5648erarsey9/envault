"""Tests for envault.pin"""

import pytest

from envault.vault import set_secret
from envault.pin import pin_secret, unpin_secret, is_pinned, get_pinned_value, list_pins


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_pin_secret_returns_value(tmp_vault):
    set_secret(tmp_vault, "prod", "API_KEY", "abc123", "pass")
    val = pin_secret(tmp_vault, "prod", "API_KEY")
    assert val == "abc123"


def test_is_pinned_after_pin(tmp_vault):
    set_secret(tmp_vault, "prod", "API_KEY", "abc123", "pass")
    pin_secret(tmp_vault, "prod", "API_KEY")
    assert is_pinned(tmp_vault, "prod", "API_KEY") is True


def test_is_not_pinned_by_default(tmp_vault):
    assert is_pinned(tmp_vault, "prod", "API_KEY") is False


def test_get_pinned_value(tmp_vault):
    set_secret(tmp_vault, "prod", "TOKEN", "secret", "pass")
    pin_secret(tmp_vault, "prod", "TOKEN")
    assert get_pinned_value(tmp_vault, "prod", "TOKEN") == "secret"


def test_get_pinned_value_missing_returns_none(tmp_vault):
    assert get_pinned_value(tmp_vault, "prod", "MISSING") is None


def test_unpin_removes_pin(tmp_vault):
    set_secret(tmp_vault, "prod", "API_KEY", "abc", "pass")
    pin_secret(tmp_vault, "prod", "API_KEY")
    result = unpin_secret(tmp_vault, "prod", "API_KEY")
    assert result is True
    assert is_pinned(tmp_vault, "prod", "API_KEY") is False


def test_unpin_nonexistent_returns_false(tmp_vault):
    assert unpin_secret(tmp_vault, "prod", "NOPE") is False


def test_list_pins(tmp_vault):
    set_secret(tmp_vault, "prod", "A", "1", "pass")
    set_secret(tmp_vault, "prod", "B", "2", "pass")
    pin_secret(tmp_vault, "prod", "A")
    pin_secret(tmp_vault, "prod", "B")
    pins = list_pins(tmp_vault, "prod")
    assert sorted(pins) == ["A", "B"]


def test_pin_nonexistent_key_raises(tmp_vault):
    with pytest.raises(KeyError, match="MISSING"):
        pin_secret(tmp_vault, "prod", "MISSING")


def test_pins_are_env_scoped(tmp_vault):
    set_secret(tmp_vault, "prod", "KEY", "val", "pass")
    pin_secret(tmp_vault, "prod", "KEY")
    assert is_pinned(tmp_vault, "staging", "KEY") is False
