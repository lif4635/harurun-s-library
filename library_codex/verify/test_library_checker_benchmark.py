import hashlib
import subprocess
import sys

import pytest

from library_codex.benchmarks.library_checker import atomic_write, select_latest, verify_source
from library_codex.benchmarks.library_checker_cases import make_case, standalone_source


@pytest.mark.parametrize("problem,families", [
    ("set_xor_min", ["random", "dense", "duplicates", "prefix"]),
    ("vertex_add_subtree_sum", ["random", "chain", "star", "balanced"]),
])
def test_generated_inputs_and_standalone(problem, families, tmp_path):
    for family in families:
        data, expected = make_case(problem, 80, family, 91)
        assert (data, expected) == make_case(problem, 80, family, 91)
        names = [problem, "subtree_dsu"] if problem == "vertex_add_subtree_sum" else [problem]
        for name in names:
            script = tmp_path / "submission.py"
            script.write_bytes(standalone_source(name))
            actual = subprocess.check_output([sys.executable, "-I", str(script)], input=data, cwd=tmp_path, timeout=20)
            assert actual.split() == expected


def test_snapshot_validation_and_atomic_write(tmp_path):
    source = b"print(1)\n"
    atomic_write(tmp_path / "1.py", source)
    row = {"sourceFile": "1.py", "sourceSha256": hashlib.sha256(source).hexdigest()}
    assert verify_source(tmp_path, row).read_bytes() == source
    atomic_write(tmp_path / "1.py", b"changed")
    with pytest.raises(ValueError, match="hash"):
        verify_source(tmp_path, row)
    with pytest.raises(ValueError, match="path"):
        verify_source(tmp_path, dict(row, sourceFile="../other.py"))
    base = dict(problem_name="set_xor_min", lang="pypy3", status="AC", is_latest=True)
    rows = [base, dict(base, status="WA"), dict(base, is_latest=False), dict(base, lang="cpp")]
    assert select_latest(rows, "set_xor_min", "pypy3") == [base]


def test_failed_replacement_preserves_previous_file(tmp_path, monkeypatch):
    from library_codex.benchmarks import library_checker

    path = tmp_path / "snapshot.json"
    atomic_write(path, b"previous")

    def fail(source, target):
        raise OSError("replacement failed")

    monkeypatch.setattr(library_checker.os, "replace", fail)
    with pytest.raises(OSError, match="replacement"):
        atomic_write(path, b"new")
    assert path.read_bytes() == b"previous"
    assert list(tmp_path.iterdir()) == [path]
