import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from library_codex.benchmarks import official_probe as module


def test_selected_generators():
    problem = SimpleNamespace(config={"tests": [{"name": "example.in", "number": 2}, {"name": "random.cpp", "number": 3}]})
    assert module.selected_generators(problem, ["random_02", "example_00"]) == [
        ("random_02", "random.cpp", 2), ("example_00", "example.in", 0)]
    for names in ([], ["random_03"], ["random_00", "random_00"], ["../random_00"]):
        with pytest.raises(ValueError):
            module.selected_generators(problem, names)


@pytest.mark.parametrize("status", ["selected_cases_passed", "selected_cases_failed"])
def test_cli_exit_status(monkeypatch, status):
    monkeypatch.setattr(module.sys, "argv", [
        "official_probe.py", "p", "--official", ".", "--cases", "example_00",
    ])
    monkeypatch.setattr(module, "probe", lambda args: {"status": status})
    if status == "selected_cases_failed":
        with pytest.raises(SystemExit) as error:
            module.main()
        assert error.value.code == 1
    else:
        module.main()


@pytest.mark.parametrize("mode,expected", [
    ("pass", "selected_cases_passed"),
    ("slow", "selected_cases_failed"),
    ("timeout", "selected_cases_failed"),
    ("checker_timeout", "selected_cases_failed"),
])
def test_probe_preserves_scope_and_failures(tmp_path, monkeypatch, mode, expected):
    source = tmp_path / "source.py"
    source.write_text("print(1)")
    problem = SimpleNamespace(
        config={"tests": [{"name": "example.in", "number": 2}], "timelimit": 1},
        basedir=tmp_path, rootdir=tmp_path, checker=tmp_path / "checker.cpp",
        problem_version=lambda: "version",
    )
    monkeypatch.setattr(module, "load_official", lambda path: {"p": problem})
    monkeypatch.setattr(module, "runtime_info", lambda python: {"runtime": "PyPy"})
    monkeypatch.setattr(module, "build_solution", lambda name: (source, ["module"]))
    monkeypatch.setattr(module, "prepare_cases", lambda p, names: None)
    monkeypatch.setattr(module, "file_digest", lambda path: "hash")
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **kw: "revision")

    def measure(*args):
        if mode == "timeout":
            raise subprocess.TimeoutExpired("solution", 2)
        return (1.5 if mode == "slow" else 0.5), 100

    def checker(*args, **kwargs):
        if mode == "checker_timeout":
            raise subprocess.TimeoutExpired("checker", 180)
        return SimpleNamespace(returncode=0, stderr=b"")

    monkeypatch.setattr(module, "measure", measure)
    monkeypatch.setattr(module.subprocess, "run", checker)
    output = tmp_path / "probe.json"
    args = SimpleNamespace(repeat=2, timeout=2, official=tmp_path, problem="p",
                           cases=["example_00"], python="pypy3", output=output)
    module.probe(args)
    report = json.loads(output.read_text())
    assert report["status"] == expected
    assert report["officialCases"] == 2
    assert report["selectedCases"] == ["example_00"]
    assert len(report["results"]) == 2
    assert report["status"] != "local_passed"
    if mode == "checker_timeout":
        assert report["results"][0]["status"] == "CHECKER_ERROR"
    assert not (tmp_path / "manifest.json").exists()
