import hashlib
import subprocess
import sys

import pytest

from library_codex.benchmarks.library_checker import atomic_write, select_latest, verify_source
from library_codex.benchmarks.library_checker_cases import make_case, standalone_source
from library_codex.benchmarks.lc_problems import PROBLEMS, problem_module, standalone


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


@pytest.mark.parametrize("problem", PROBLEMS)
def test_problem_solutions_against_independent_oracles(problem):
    source = standalone_source(problem)
    assert b"from library_codex." not in source
    namespace = {"__name__": "submission"}
    exec(source.rsplit(b"\nsolve()", 1)[0], namespace)
    module = problem_module(problem)
    import io
    from contextlib import redirect_stdout

    for n in (1, 2, 17, 64, 129):
        if n < getattr(module, "MIN_SIZE", 1):
            continue
        for family in module.FAMILIES:
            data, expected = make_case(problem, n, family, 1928 + n)
            original = sys.stdin
            sys.stdin = io.TextIOWrapper(io.BytesIO(data))
            output = io.StringIO()
            try:
                with redirect_stdout(output):
                    namespace["solve"]()
            finally:
                sys.stdin = original
            assert output.getvalue().encode().split() == expected, (problem, n, family)


@pytest.mark.parametrize("problem,variant", [
    (problem, variant) for problem in PROBLEMS
    for variant in getattr(problem_module(problem), "VARIANTS", {})
])
def test_problem_variants_are_standalone(problem, variant, tmp_path):
    for family in problem_module(problem).FAMILIES:
        data, expected = make_case(problem, 129, family, 910)
        script = tmp_path / "submission.py"
        script.write_bytes(standalone(problem, variant))
        actual = subprocess.check_output([sys.executable, "-I", str(script)], input=data, cwd=tmp_path, timeout=20)
        assert actual.split() == expected


def test_problem_input_limits():
    with pytest.raises(ValueError, match="constraints"):
        make_case("unionfind", 200001, "random", 1)
    with pytest.raises(ValueError, match="constraints"):
        make_case("lca", 1, "random", 1)
    with pytest.raises(ValueError, match="constraints"):
        make_case("composition_of_formal_power_series", 8001, "dense", 1)
    with pytest.raises(ValueError, match="constraints"):
        make_case("composition_of_formal_power_series_large", 131073, "dense", 1)
    with pytest.raises(ValueError, match="family"):
        make_case("point_add_range_sum", 10, "missing", 1)


def test_compare_saved_baseline_and_candidate(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from library_codex.benchmarks import library_checker

    problem = "composition_of_formal_power_series_large"
    code = standalone_source(problem)
    script = tmp_path / "reference.py"
    script.write_bytes(code)
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps(dict(language="pypy3", problem=problem, submissions=[
        dict(id=1, sourceFile=script.name, sourceSha256=hashlib.sha256(code).hexdigest())
    ])))
    calls = []
    expected = make_case(problem, 17, "dense", 91)[1]

    def run(command, input_path, timeout, directory):
        calls.append(Path(command[1]).stem)
        return expected, 0.25, 100

    from pathlib import Path
    monkeypatch.setattr(library_checker, "run_once", run)
    output = tmp_path / "report.json"
    library_checker.compare(SimpleNamespace(snapshot=snapshot, reviewed=[1], baseline=script,
        candidate=script, no_variants=True, python=sys.executable, repeat=2, seed=91,
        families=["dense"], size=17, timeout=10, output=output))
    report = json.loads(output.read_text())
    assert set(report["sourceHashes"]) == {"1", "library", "before", "candidate"}
    assert len(calls) == 8
    assert all(calls.count(name) == 2 for name in report["sourceHashes"])
    assert report["results"][0]["bruteChecked"]
