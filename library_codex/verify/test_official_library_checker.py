import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_library_checker as lc


def test_cases_are_complete_and_ordered():
    problem = SimpleNamespace(config={"tests": [{"name": "example.in", "number": 2}, {"name": "random.cpp", "number": 3}]})
    assert lc.case_names(problem) == ["example_00", "example_01", "random_00", "random_01", "random_02"]
    problem.config["tests"] = []
    with pytest.raises(ValueError):
        lc.case_names(problem)


def test_source_or_official_change_invalidates_verification():
    original = ["problem", "source", "runtime", 2.0, "runner"]
    key = lc.verification_key(*original)
    for index in range(5):
        changed = original[:]
        changed[index] = 3.0 if index == 3 else "changed"
        assert lc.verification_key(*changed) != key


def test_incomplete_or_failed_reports_are_not_cached():
    report = {"status": "local_passed", "expectedCases": 2,
              "cases": [{"name": "a", "status": "AC"}, {"name": "b", "status": "AC"}]}
    assert lc.complete_pass(report, ["a", "b"])
    assert not lc.complete_pass(report, ["a", "b", "c"])
    assert not lc.complete_pass(report, ["b", "a"])
    report["cases"][1]["status"] = "TLE"
    assert not lc.complete_pass(report, ["a", "b"])
    report["cases"].pop()
    assert not lc.complete_pass(report, ["a", "b"])


def test_generation_tracks_dependencies_and_stale_exports(tmp_path, monkeypatch):
    monkeypatch.setattr(lc, "SUITE", tmp_path)
    (tmp_path / "drivers").mkdir()
    driver = tmp_path / "drivers" / "sample.py"
    driver.write_text("print(1)\n")
    path, _ = lc.build_solution("sample")
    assert path.read_text() == "print(1)\n"
    driver.write_text("print(2)\n")
    assert "stale standalone solution: sample" in lc.check_solutions()
    lc.build_solution("sample")
    assert path.read_text() == "print(2)\n"
    dependency = lc.ROOT / "union_find" / "UnionFind.py"
    source = dependency.read_text(encoding="utf-8")
    original = Path.read_text

    def changed(path, *args, **kwargs):
        if path == dependency:
            return source.replace("class UnionFind:", "TEST_VALUE = 7\n\nclass UnionFind:")
        return original(path, *args, **kwargs)

    before, _ = lc.solution("unionfind")
    monkeypatch.setattr(Path, "read_text", changed)
    after, _ = lc.solution("unionfind")
    assert before != after


def test_atomic_json_failure_preserves_previous_result(tmp_path, monkeypatch):
    import os

    target = tmp_path / "result.json"
    lc.save_json(target, {"status": "local_passed"})

    def fail(*args):
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        lc.save_json(target, {"status": "incomplete"})
    assert json.loads(target.read_text())["status"] == "local_passed"
    assert list(tmp_path.iterdir()) == [target]


def test_associative_array_integer_keys_and_overwrite(tmp_path):
    source, _ = lc.solution("associative_array")
    path = tmp_path / "main.py"
    path.write_text(source)
    result = subprocess.run([sys.executable, str(path)], input="7\n0 001 7\n1 1\n0 1 0\n1 001\n1 2\n0 1000000000000000000 9\n1 1000000000000000000\n", text=True, capture_output=True, check=True)
    assert result.stdout.split() == ["7", "0", "0", "9"]


@pytest.mark.parametrize("exit_code,status", [(0, "AC"), (1, "WA"), (2, "WA"), (3, "CHECKER_ERROR")])
def test_checker_result_and_argument_order(tmp_path, monkeypatch, exit_code, status):
    stdin, expected, actual = [tmp_path / name for name in ("input", "expected", "actual")]
    stdin.write_text("1 2\n")
    expected.write_text("3\n")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        if len(commands) == 1:
            kwargs["stdout"].write(b"3\n")
            return subprocess.CompletedProcess(command, 0, stderr=b"")
        return subprocess.CompletedProcess(command, exit_code, stdout=b"", stderr=b"checker result")

    monkeypatch.setattr(subprocess, "run", run)
    result = lc.judge_case(["pypy3", "main.py"], tmp_path / "checker", stdin, expected, actual, 2)
    assert result["status"] == status
    assert commands[1][1:] == [str(stdin), str(actual), str(expected)]


def test_timeout_is_not_an_ac(tmp_path, monkeypatch):
    stdin = tmp_path / "input"
    stdin.write_text("1 2\n")

    def timeout(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 1)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert lc.judge_case(["pypy3"], tmp_path / "checker", stdin, tmp_path / "expected", tmp_path / "actual", 1)["status"] == "TLE"


def test_reuse_requires_official_hash_match(tmp_path):
    root, old = tmp_path / "new", tmp_path / "old"
    target = root / "sample" / "aplusb"
    source = old / "sample" / "aplusb"
    target.mkdir(parents=True)
    (source / "in").mkdir(parents=True)
    (source / "out").mkdir()
    (source / "in" / "example_00.in").write_bytes(b"1 2\n")
    (source / "out" / "example_00.out").write_bytes(b"wrong\n")
    (target / "hash.json").write_text(json.dumps({"example_00.in": lc.digest(b"1 2\n"), "example_00.out": lc.digest(b"3\n")}))
    problem = SimpleNamespace(rootdir=root, basedir=target, config={"tests": [{"name": "example.in", "number": 1}]})
    assert lc.reuse_tests(problem, old) == 1
    assert (target / "in" / "example_00.in").read_bytes() == b"1 2\n"
    assert not (target / "out" / "example_00.out").exists()
    assert lc.reuse_tests(problem, old) == 0


@pytest.mark.parametrize("name", ["aplusb", "scc", "unionfind", "convolution_mod"])
def test_solution_is_standalone(name):
    source, modules = lc.solution(name)
    compile(source, name, "exec")
    assert "from library_codex" not in source
    assert source == lc.solution(name)[0]
    if name == "aplusb":
        assert modules == []
    else:
        assert modules


@pytest.mark.parametrize("name,data,expected", [
    ("assignment", "2\n1 8\n5 2\n", "3 0 1"),
    ("biconnected_components", "1 0\n", "1 1 0"),
    ("three_edge_connected_components", "2 3\n0 1\n0 1\n0 1\n", "1 2 0 1"),
    ("incremental_scc", "2 2\n2 3\n0 1\n1 0\n", "0 6"),
    ("general_weighted_matching", "3 3\n0 1 1\n1 2 4\n0 2 9\n", "1 9 0 2"),
    ("counting_spanning_tree_directed", "3 4 0\n0 1\n0 1\n1 2\n0 2\n", "4"),
    ("counting_spanning_tree_undirected", "3 3\n0 1\n1 2\n2 0\n", "3"),
    ("rectangle_sum", "3 4\n0 0 2\n1 1 3\n1 1 5\n0 0 1 1\n1 1 2 2\n0 0 2 2\n2 2 3 3\n", "2 8 10 0"),
    ("static_convex_hull", "3\n0\n3\n1 2\n1 2\n1 2\n3\n0 0\n1 0\n2 0\n", "0 1 1 2 2 0 0 2 0"),
    ("sort_points_by_argument", "5\n-1 0\n0 1\n1 0\n0 0\n0 -1\n", "0 -1 0 0 1 0 0 1 -1 0"),
    ("gcd_of_gaussian_integers", "2\n0 0 0 0\n3 4 0 0\n", "0 0 3 4"),
    ("closest_pair", "2\n3\n2 2\n2 2\n9 9\n3\n0 0\n10 0\n11 0\n", "0 1 1 2"),
    ("furthest_pair", "2\n3\n2 2\n2 2\n2 2\n3\n0 0\n10 0\n11 0\n", "0 1 0 2"),
    ("many_aplusb", "2\n0 0\n1000000000000000000 1000000000000000000\n", "0 2000000000000000000"),
    ("many_aplusb_128bit", "2\n-10000000000000000000000000000000000000 1\n-7 7\n", "-9999999999999999999999999999999999999 0"),
])
def test_driver_input_output_contracts(tmp_path, name, data, expected):
    source, _ = lc.solution(name)
    assert "from library_codex" not in source
    path = tmp_path / "main.py"
    path.write_text(source)
    result = subprocess.run([sys.executable, str(path)], input=data, text=True,
                            capture_output=True, check=True, cwd=tmp_path, timeout=10)
    assert result.stdout.split() == expected.split()
