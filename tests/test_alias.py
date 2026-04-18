import pytest
import json
from pathlib import Path
from envault.alias import set_alias, get_alias, remove_alias, list_aliases, resolve_alias


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(json.dumps({}))
    return str(vault_file)


def test_set_alias_returns_entry(tmp_vault):
    entry = set_alias(tmp_vault, "db", "DATABASE_URL", "prod")
    assert entry["key"] == "DATABASE_URL"
    assert entry["env"] == "prod"


def test_get_alias_after_set(tmp_vault):
    set_alias(tmp_vault, "db", "DATABASE_URL", "prod")
    result = get_alias(tmp_vault, "db")
    assert result == {"key": "DATABASE_URL", "env": "prod"}


def test_get_alias_missing_returns_none(tmp_vault):
    assert get_alias(tmp_vault, "nope") is None


def test_set_alias_empty_name_raises(tmp_vault):
    with pytest.raises(ValueError):
        set_alias(tmp_vault, "  ", "KEY", "dev")


def test_remove_alias_returns_true(tmp_vault):
    set_alias(tmp_vault, "db", "DATABASE_URL", "prod")
    assert remove_alias(tmp_vault, "db") is True
    assert get_alias(tmp_vault, "db") is None


def test_remove_missing_alias_returns_false(tmp_vault):
    assert remove_alias(tmp_vault, "ghost") is False


def test_list_aliases_empty(tmp_vault):
    assert list_aliases(tmp_vault) == {}


def test_list_aliases_multiple(tmp_vault):
    set_alias(tmp_vault, "db", "DATABASE_URL", "prod")
    set_alias(tmp_vault, "cache", "REDIS_URL", "staging")
    result = list_aliases(tmp_vault)
    assert len(result) == 2
    assert "db" in result
    assert "cache" in result


def test_resolve_alias_returns_tuple(tmp_vault):
    set_alias(tmp_vault, "db", "DATABASE_URL", "prod")
    assert resolve_alias(tmp_vault, "db") == ("DATABASE_URL", "prod")


def test_resolve_missing_alias_returns_none(tmp_vault):
    assert resolve_alias(tmp_vault, "missing") is None
