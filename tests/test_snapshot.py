"""Tests for envault.snapshot."""

import os
import pytest

from envault.vault import set_secret, get_secret
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot


PASSWORD = "test-pass"


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def _populate(vault_path, env="prod"):
    set_secret(vault_path, env, "DB_URL", "postgres://localhost/db", PASSWORD)
    set_secret(vault_path, env, "API_KEY", "abc123", PASSWORD)


def test_create_snapshot_returns_label(tmp_vault):
    _populate(tmp_vault)
    label = create_snapshot(tmp_vault, "prod", PASSWORD)
    assert isinstance(label, str)
    assert len(label) > 0


def test_create_snapshot_with_custom_label(tmp_vault):
    _populate(tmp_vault)
    label = create_snapshot(tmp_vault, "prod", PASSWORD, label="v1")
    assert label == "v1"


def test_create_snapshot_file_exists(tmp_vault):
    _populate(tmp_vault)
    label = create_snapshot(tmp_vault, "prod", PASSWORD, label="v1")
    snap_dir = os.path.join(os.path.dirname(tmp_vault), ".snapshots")
    assert os.path.isfile(os.path.join(snap_dir, "prod__v1.json"))


def test_list_snapshots_empty(tmp_vault):
    assert list_snapshots(tmp_vault, "prod") == []


def test_list_snapshots_returns_metadata(tmp_vault):
    _populate(tmp_vault)
    create_snapshot(tmp_vault, "prod", PASSWORD, label="snap1")
    create_snapshot(tmp_vault, "prod", PASSWORD, label="snap2")
    snaps = list_snapshots(tmp_vault, "prod")
    assert len(snaps) == 2
    labels = {s["label"] for s in snaps}
    assert labels == {"snap1", "snap2"}


def test_list_snapshots_key_count(tmp_vault):
    _populate(tmp_vault)
    create_snapshot(tmp_vault, "prod", PASSWORD, label="snap1")
    snaps = list_snapshots(tmp_vault, "prod")
    assert snaps[0]["key_count"] == 2


def test_restore_snapshot_writes_secrets(tmp_vault):
    _populate(tmp_vault)
    create_snapshot(tmp_vault, "prod", PASSWORD, label="backup")

    # Wipe and restore into a different env
    written = restore_snapshot(tmp_vault, "prod", PASSWORD, "backup", overwrite=True)
    assert written == 2
    assert get_secret(tmp_vault, "prod", "DB_URL", PASSWORD) == "postgres://localhost/db"


def test_restore_snapshot_skips_existing_by_default(tmp_vault):
    _populate(tmp_vault)
    create_snapshot(tmp_vault, "prod", PASSWORD, label="backup")
    # All keys already exist → nothing written
    written = restore_snapshot(tmp_vault, "prod", PASSWORD, "backup", overwrite=False)
    assert written == 0


def test_restore_missing_snapshot_raises(tmp_vault):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(tmp_vault, "prod", PASSWORD, "nonexistent")
