import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "prepare_checkpoint.py"
SPEC = importlib.util.spec_from_file_location("prepare_checkpoint", SCRIPT)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def test_changed_profile_uses_affected_checks_and_benchmarks():
    command = PREPARE.check_command("changed")
    assert command[-2].endswith("check_changed.py")
    assert command[-1] == "--benchmarks"


def test_release_profile_uses_full_checks():
    command = PREPARE.check_command("full")
    assert command[-3].endswith("check_library.py")
    assert command[-2:] == ["--profile", "full"]


def test_site_sync_rejects_an_unrelated_directory(tmp_path):
    with pytest.raises(ValueError, match="missing"):
        PREPARE.site_sync_command(tmp_path)
