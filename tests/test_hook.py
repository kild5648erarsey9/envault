import pytest
from pathlib import Path
from envault.hook import set_hook, get_hook, delete_hook, list_hooks


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_hook_returns_entry(tmp_vault):
    entry = set_hook(tmp_vault, "DB_PASS", "pre", "echo pre")
    assert entry["pre"] == "echo pre"


def test_get_hook_after_set(tmp_vault):
    set_hook(tmp_vault, "DB_PASS", "post", "echo post")
    assert get_hook(tmp_vault, "DB_PASS", "post") == "echo post"


def test_get_hook_missing_returns_none(tmp_vault):
    assert get_hook(tmp_vault, "MISSING", "pre") is None


def test_set_hook_invalid_stage_raises(tmp_vault):
    with pytest.raises(ValueError, match="stage"):
        set_hook(tmp_vault, "KEY", "during", "echo x")


def test_set_hook_empty_command_raises(tmp_vault):
    with pytest.raises(ValueError, match="command"):
        set_hook(tmp_vault, "KEY", "pre", "   ")


def test_delete_hook_single_stage(tmp_vault):
    set_hook(tmp_vault, "API_KEY", "pre", "echo pre")
    set_hook(tmp_vault, "API_KEY", "post", "echo post")
    delete_hook(tmp_vault, "API_KEY", "pre")
    assert get_hook(tmp_vault, "API_KEY", "pre") is None
    assert get_hook(tmp_vault, "API_KEY", "post") == "echo post"


def test_delete_hook_all_stages(tmp_vault):
    set_hook(tmp_vault, "API_KEY", "pre", "echo pre")
    set_hook(tmp_vault, "API_KEY", "post", "echo post")
    delete_hook(tmp_vault, "API_KEY")
    assert list_hooks(tmp_vault) == {}


def test_delete_hook_nonexistent_is_noop(tmp_vault):
    delete_hook(tmp_vault, "GHOST")  # should not raise


def test_list_hooks_empty(tmp_vault):
    assert list_hooks(tmp_vault) == {}


def test_list_hooks_multiple_keys(tmp_vault):
    set_hook(tmp_vault, "A", "pre", "cmd_a")
    set_hook(tmp_vault, "B", "post", "cmd_b")
    hooks = list_hooks(tmp_vault)
    assert "A" in hooks and "B" in hooks
