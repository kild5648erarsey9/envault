import pytest
from pathlib import Path
from envault.dependency import (
    add_dependency, remove_dependency, get_dependencies,
    get_dependents, list_all_dependencies
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_add_dependency_returns_list(tmp_vault):
    deps = add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    assert deps == ["MASTER_KEY"]


def test_add_multiple_dependencies(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    deps = add_dependency(tmp_vault, "APP_KEY", "SALT")
    assert "MASTER_KEY" in deps
    assert "SALT" in deps


def test_add_duplicate_dependency_ignored(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    deps = add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    assert deps.count("MASTER_KEY") == 1


def test_add_self_dependency_raises(tmp_vault):
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency(tmp_vault, "APP_KEY", "APP_KEY")


def test_add_empty_key_raises(tmp_vault):
    with pytest.raises(ValueError):
        add_dependency(tmp_vault, "", "MASTER_KEY")


def test_get_dependencies_after_add(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    assert get_dependencies(tmp_vault, "APP_KEY") == ["MASTER_KEY"]


def test_get_dependencies_missing_key_returns_empty(tmp_vault):
    assert get_dependencies(tmp_vault, "NONEXISTENT") == []


def test_get_dependents(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    add_dependency(tmp_vault, "OTHER_KEY", "MASTER_KEY")
    dependents = get_dependents(tmp_vault, "MASTER_KEY")
    assert "APP_KEY" in dependents
    assert "OTHER_KEY" in dependents


def test_get_dependents_none(tmp_vault):
    assert get_dependents(tmp_vault, "ORPHAN") == []


def test_remove_dependency(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    add_dependency(tmp_vault, "APP_KEY", "SALT")
    remaining = remove_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    assert "MASTER_KEY" not in remaining
    assert "SALT" in remaining


def test_remove_last_dependency_cleans_key(tmp_vault):
    add_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    remove_dependency(tmp_vault, "APP_KEY", "MASTER_KEY")
    all_deps = list_all_dependencies(tmp_vault)
    assert "APP_KEY" not in all_deps


def test_list_all_dependencies(tmp_vault):
    add_dependency(tmp_vault, "A", "B")
    add_dependency(tmp_vault, "C", "D")
    all_deps = list_all_dependencies(tmp_vault)
    assert "A" in all_deps
    assert "C" in all_deps
