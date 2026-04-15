"""Tests for envault.template."""
from __future__ import annotations

import pytest

from envault.vault import set_secret
from envault.template import render_string, render_file, MissingSecretError


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


PASSWORD = "test-password"
ENV = "staging"


def _seed(vault_path: str) -> None:
    set_secret(vault_path, ENV, "DB_HOST", "db.internal", PASSWORD)
    set_secret(vault_path, ENV, "API_KEY", "s3cr3t", PASSWORD)
    set_secret(vault_path, ENV, "PORT", "5432", PASSWORD)


def test_render_simple_substitution(tmp_vault):
    _seed(tmp_vault)
    result = render_string("host={{ DB_HOST }}", tmp_vault, ENV, PASSWORD)
    assert result == "host=db.internal"


def test_render_multiple_placeholders(tmp_vault):
    _seed(tmp_vault)
    tmpl = "postgresql://{{ DB_HOST }}:{{ PORT }}/mydb"
    result = render_string(tmpl, tmp_vault, ENV, PASSWORD)
    assert result == "postgresql://db.internal:5432/mydb"


def test_render_no_whitespace_inside_braces(tmp_vault):
    _seed(tmp_vault)
    result = render_string("key={{API_KEY}}", tmp_vault, ENV, PASSWORD)
    assert result == "key=s3cr3t"


def test_render_missing_key_strict_raises(tmp_vault):
    _seed(tmp_vault)
    with pytest.raises(MissingSecretError, match="MISSING_KEY"):
        render_string("{{ MISSING_KEY }}", tmp_vault, ENV, PASSWORD)


def test_render_missing_key_non_strict_leaves_placeholder(tmp_vault):
    _seed(tmp_vault)
    result = render_string(
        "{{ MISSING_KEY }}", tmp_vault, ENV, PASSWORD, strict=False
    )
    assert result == "{{ MISSING_KEY }}"


def test_render_no_placeholders(tmp_vault):
    _seed(tmp_vault)
    plain = "no placeholders here"
    assert render_string(plain, tmp_vault, ENV, PASSWORD) == plain


def test_render_file_reads_and_substitutes(tmp_vault, tmp_path):
    _seed(tmp_vault)
    src = tmp_path / "config.tmpl"
    src.write_text("API_KEY={{ API_KEY }}\nDB={{ DB_HOST }}", encoding="utf-8")
    result = render_file(src, tmp_vault, ENV, PASSWORD)
    assert result == "API_KEY=s3cr3t\nDB=db.internal"


def test_render_file_writes_dest(tmp_vault, tmp_path):
    _seed(tmp_vault)
    src = tmp_path / "config.tmpl"
    dest = tmp_path / "config.env"
    src.write_text("PORT={{ PORT }}", encoding="utf-8")
    render_file(src, tmp_vault, ENV, PASSWORD, dest=dest)
    assert dest.read_text(encoding="utf-8") == "PORT=5432"


def test_render_file_missing_key_raises(tmp_vault, tmp_path):
    _seed(tmp_vault)
    src = tmp_path / "bad.tmpl"
    src.write_text("{{ NOPE }}", encoding="utf-8")
    with pytest.raises(MissingSecretError):
        render_file(src, tmp_vault, ENV, PASSWORD)
