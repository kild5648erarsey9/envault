"""Tests for envault/import_.py"""

import json
import os
import pytest

from envault.import_ import _parse_dotenv, _parse_json, import_secrets
from envault.vault import get_secret, set_secret


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


# --- _parse_dotenv ---

def test_parse_dotenv_basic():
    content = "KEY=value\nFOO=bar"
    assert _parse_dotenv(content) == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_strips_quotes():
    content = 'SECRET="hello world"\nTOKEN=\'abc\''
    result = _parse_dotenv(content)
    assert result["SECRET"] == "hello world"
    assert result["TOKEN"] == "abc"


def test_parse_dotenv_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=val"
    assert _parse_dotenv(content) == {"KEY": "val"}


def test_parse_dotenv_equals_in_value():
    content = "KEY=a=b=c"
    assert _parse_dotenv(content) == {"KEY": "a=b=c"}


# --- _parse_json ---

def test_parse_json_basic():
    data = json.dumps({"A": "1", "B": "2"})
    assert _parse_json(data) == {"A": "1", "B": "2"}


def test_parse_json_coerces_values_to_str():
    data = json.dumps({"PORT": 8080, "DEBUG": True})
    result = _parse_json(data)
    assert result["PORT"] == "8080"
    assert result["DEBUG"] == "True"


def test_parse_json_non_dict_raises():
    with pytest.raises(ValueError, match="top-level object"):
        _parse_json(json.dumps(["a", "b"]))


# --- import_secrets ---

def test_import_secrets_from_dotenv(tmp_vault, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_URL=postgres://localhost\nSECRET_KEY=abc123\n")
    imported, skipped = import_secrets(tmp_vault, "prod", "pass", str(env_file))
    assert imported == 2
    assert skipped == 0
    assert get_secret(tmp_vault, "prod", "DB_URL", "pass") == "postgres://localhost"


def test_import_secrets_from_json(tmp_vault, tmp_path):
    json_file = tmp_path / "secrets.json"
    json_file.write_text(json.dumps({"TOKEN": "xyz", "PORT": "9000"}))
    imported, skipped = import_secrets(tmp_vault, "staging", "pw", str(json_file), fmt="json")
    assert imported == 2
    assert get_secret(tmp_vault, "staging", "TOKEN", "pw") == "xyz"


def test_import_secrets_skip_existing(tmp_vault, tmp_path):
    set_secret(tmp_vault, "dev", "KEY", "original", "pw")
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new_value\n")
    imported, skipped = import_secrets(tmp_vault, "dev", "pw", str(env_file), overwrite=False)
    assert imported == 0
    assert skipped == 1
    assert get_secret(tmp_vault, "dev", "KEY", "pw") == "original"


def test_import_secrets_overwrite_existing(tmp_vault, tmp_path):
    set_secret(tmp_vault, "dev", "KEY", "original", "pw")
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=updated\n")
    imported, skipped = import_secrets(tmp_vault, "dev", "pw", str(env_file), overwrite=True)
    assert imported == 1
    assert skipped == 0
    assert get_secret(tmp_vault, "dev", "KEY", "pw") == "updated"
