"""Tests for envault.redact module."""

import pytest

from envault.redact import (
    is_redacted,
    list_redacted,
    mark_redacted,
    mask_value,
    redact_text,
    unmark_redacted,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_mark_redacted_returns_sorted_list(tmp_vault):
    result = mark_redacted(tmp_vault, "DB_PASSWORD")
    assert result == ["DB_PASSWORD"]


def test_mark_multiple_keys(tmp_vault):
    mark_redacted(tmp_vault, "SECRET_B")
    result = mark_redacted(tmp_vault, "SECRET_A")
    assert result == ["SECRET_A", "SECRET_B"]


def test_mark_duplicate_is_idempotent(tmp_vault):
    mark_redacted(tmp_vault, "API_KEY")
    result = mark_redacted(tmp_vault, "API_KEY")
    assert result.count("API_KEY") == 1


def test_is_redacted_true_after_mark(tmp_vault):
    mark_redacted(tmp_vault, "TOKEN")
    assert is_redacted(tmp_vault, "TOKEN") is True


def test_is_not_redacted_by_default(tmp_vault):
    assert is_redacted(tmp_vault, "SOME_KEY") is False


def test_unmark_redacted_removes_key(tmp_vault):
    mark_redacted(tmp_vault, "DB_PASS")
    result = unmark_redacted(tmp_vault, "DB_PASS")
    assert "DB_PASS" not in result
    assert is_redacted(tmp_vault, "DB_PASS") is False


def test_unmark_nonexistent_key_is_safe(tmp_vault):
    result = unmark_redacted(tmp_vault, "GHOST_KEY")
    assert result == []


def test_list_redacted_empty(tmp_vault):
    assert list_redacted(tmp_vault) == []


def test_list_redacted_returns_all_keys(tmp_vault):
    mark_redacted(tmp_vault, "Z_KEY")
    mark_redacted(tmp_vault, "A_KEY")
    assert list_redacted(tmp_vault) == ["A_KEY", "Z_KEY"]


def test_mask_value_returns_mask():
    assert mask_value("supersecret") == "***"


def test_mask_value_empty_string():
    assert mask_value("") == "***"


def test_mask_value_partial_reveals_suffix():
    result = mask_value("supersecret", partial=True)
    assert result == "***cret"


def test_mask_value_partial_short_value():
    # value shorter than partial chars — still fully masked
    result = mask_value("ab", partial=True)
    assert result == "***"


def test_mask_value_custom_mask():
    assert mask_value("hello", mask="[HIDDEN]") == "[HIDDEN]"


def test_redact_text_replaces_secret_values():
    secrets = {"KEY": "hunter2"}
    result = redact_text("password is hunter2 ok?", secrets)
    assert "hunter2" not in result
    assert "***" in result


def test_redact_text_multiple_secrets():
    secrets = {"A": "alpha", "B": "beta"}
    result = redact_text("alpha and beta", secrets)
    assert "alpha" not in result
    assert "beta" not in result


def test_redact_text_no_match_unchanged():
    secrets = {"KEY": "hunter2"}
    text = "nothing sensitive here"
    assert redact_text(text, secrets) == text
