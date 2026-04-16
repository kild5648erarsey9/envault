import pytest
import json
from pathlib import Path
from envault.namespace import (
    assign_namespace, get_namespace, remove_namespace,
    list_namespaces, keys_in_namespace,
)


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(json.dumps({}))
    return str(vault_file)


def test_assign_returns_namespace(tmp_vault):
    ns = assign_namespace(tmp_vault, "DB_PASS", "database")
    assert ns == "database"


def test_get_namespace_after_assign(tmp_vault):
    assign_namespace(tmp_vault, "DB_PASS", "database")
    assert get_namespace(tmp_vault, "DB_PASS") == "database"


def test_get_namespace_missing_returns_none(tmp_vault):
    assert get_namespace(tmp_vault, "MISSING") is None


def test_assign_strips_whitespace(tmp_vault):
    ns = assign_namespace(tmp_vault, "KEY", "  infra  ")
    assert ns == "infra"
    assert get_namespace(tmp_vault, "KEY") == "infra"


def test_assign_empty_namespace_raises(tmp_vault):
    with pytest.raises(ValueError):
        assign_namespace(tmp_vault, "KEY", "")


def test_remove_namespace(tmp_vault):
    assign_namespace(tmp_vault, "KEY", "infra")
    remove_namespace(tmp_vault, "KEY")
    assert get_namespace(tmp_vault, "KEY") is None


def test_remove_nonexistent_is_noop(tmp_vault):
    remove_namespace(tmp_vault, "GHOST")  # should not raise


def test_list_namespaces(tmp_vault):
    assign_namespace(tmp_vault, "A", "db")
    assign_namespace(tmp_vault, "B", "infra")
    assign_namespace(tmp_vault, "C", "db")
    assert list_namespaces(tmp_vault) == ["db", "infra"]


def test_list_namespaces_empty(tmp_vault):
    assert list_namespaces(tmp_vault) == []


def test_keys_in_namespace(tmp_vault):
    assign_namespace(tmp_vault, "DB_PASS", "database")
    assign_namespace(tmp_vault, "DB_USER", "database")
    assign_namespace(tmp_vault, "API_KEY", "api")
    assert keys_in_namespace(tmp_vault, "database") == ["DB_PASS", "DB_USER"]


def test_keys_in_namespace_no_match(tmp_vault):
    assign_namespace(tmp_vault, "KEY", "infra")
    assert keys_in_namespace(tmp_vault, "unknown") == []
