import json
from types import SimpleNamespace

import pytest

from library_codex.benchmarks import official_benchmark as bench


def test_select_cases_rejects_stale_or_incomplete_results():
    names = ["a", "b", "c"]
    report = dict(status="local_passed", expectedCases=3, sourceSha256="source", problemVersion="version",
                  cases=[dict(name=name, status="AC", seconds=i + 1) for i, name in enumerate(names)])
    assert bench.select_cases(report, names, "source", "version", 2) == ["c", "b"]
    assert bench.select_cases(report, names, "source", "version", 0) == ["c", "b", "a"]
    with pytest.raises(ValueError, match="stale"):
        bench.select_cases(report, names, "changed", "version", 2)
    report["cases"].pop()
    with pytest.raises(ValueError, match="complete"):
        bench.select_cases(report, names, "source", "version", 2)


def test_requires_pypy(monkeypatch):
    monkeypatch.setattr(bench.subprocess, "check_output", lambda *a, **k: "Python 3.10.14")
    with pytest.raises(ValueError, match="PyPy"):
        bench.runtime_info("python3")


def test_benchmark_records_samples_and_preserves_report_on_failure(tmp_path, monkeypatch):
    root = tmp_path / "official"
    (root / "in").mkdir(parents=True)
    (root / "out").mkdir()
    (root / "in" / "example_00.in").write_text("input")
    (root / "out" / "example_00.out").write_text("output")
    (root / "checker").write_text("checker")
    hashes = {p.name: bench.file_digest(p) for p in (root / "in" / "example_00.in", root / "out" / "example_00.out")}
    (root / "hash.json").write_text(json.dumps(hashes))
    problem = SimpleNamespace(basedir=root, rootdir=root, checker=root / "checker", problem_version=lambda: "v",
                              config=dict(timelimit=5, tests=[dict(name="example.in", number=1)]))
    suite = tmp_path / "suite"
    (suite / "results").mkdir(parents=True)
    source = "print(1)\n"
    verification = dict(status="local_passed", expectedCases=1, sourceSha256=bench.digest(source.encode()),
                        problemVersion="v", cases=[dict(name="example_00", status="AC", seconds=1)])
    (suite / "results" / "problem.json").write_text(json.dumps(verification))
    monkeypatch.setattr(bench, "SUITE", suite)
    monkeypatch.setattr(bench, "solution", lambda name: (source, []))
    monkeypatch.setattr(bench, "runtime_info", lambda runtime: dict(runtime="PyPy"))
    monkeypatch.setattr(bench.subprocess, "check_output", lambda *a, **k: "revision")
    monkeypatch.setattr(bench.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stderr=b""))
    calls = []

    def measure(command, input_path, output_path, rss_path, timeout):
        calls.append(command)
        output_path.write_text(str(len(calls)))
        return len(calls) * 0.1, 1000 + len(calls)

    monkeypatch.setattr(bench, "measure", measure)
    output = tmp_path / "benchmarks"
    report = bench.benchmark("problem", problem, "pypy3", 3, 3, output)
    assert report["results"][0]["medianSeconds"] == 0.2
    assert report["results"][0]["peakRssKiB"] == 1003
    assert len(report["results"][0]["samples"]) == 3
    bench.write_summary(output)
    assert "| 1 / 1 | 3 | 0.200 |" in (output / "README.md").read_text()
    assert "一致" in (output / "README.md").read_text()
    monkeypatch.setattr(bench, "solution", lambda name: (source + "print(2)\n", []))
    bench.write_summary(output)
    assert "要再測定" in (output / "README.md").read_text()
    monkeypatch.setattr(bench, "solution", lambda name: (source, []))
    saved = (output / "problem.json").read_bytes()
    monkeypatch.setattr(bench.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stderr=b"wrong answer"))
    with pytest.raises(ValueError, match="wrong answer"):
        bench.benchmark("problem", problem, "pypy3", 3, 3, output)
    assert (output / "problem.json").read_bytes() == saved
    (root / "in" / "example_00.in").write_text("tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        bench.benchmark("problem", problem, "pypy3", 3, 3, output)
