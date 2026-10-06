import json
from types import SimpleNamespace

import pytest

from library_codex.benchmarks import official_comparison as comparison


def setup_case(tmp_path):
    problem = tmp_path / "matching"
    (problem / "in").mkdir(parents=True)
    (problem / "out").mkdir()
    input_path = problem / "in" / "example_00.in"
    expected_path = problem / "out" / "example_00.out"
    input_path.write_text("input")
    expected_path.write_text("expected")
    (problem / "checker").write_text("checker")
    (problem / "hash.json").write_text(json.dumps({p.name: comparison.file_digest(p)
                                                  for p in (input_path, expected_path)}))
    source = tmp_path / "1.py"
    source.write_text("print(1)\n")
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps(dict(problem="matching", language="pypy3",
        submissions=[dict(id=1, sourceFile=source.name, sourceSha256=comparison.file_digest(source))])))
    return SimpleNamespace(snapshot=snapshot, reviewed=[1], problem=problem,
                           cases=["example_00"], variant=[], python="pypy3",
                           repeat=2, seed=3, timeout=30, output=tmp_path / "result.json")


def test_local_variants_without_external_submission(tmp_path, monkeypatch):
    args = setup_case(tmp_path)
    args.reviewed = []
    with pytest.raises(ValueError, match="at least one"):
        comparison.compare(args)
    args.variant = ["local=" + str(tmp_path / "1.py")]
    def measure(command, input_path, output_path, rss_path, timeout):
        output_path.write_text("1")
        return 0.25, 1024
    monkeypatch.setattr(comparison, "measure", measure)
    monkeypatch.setattr(comparison.subprocess, "check_output", lambda *a, **k: "version")
    monkeypatch.setattr(comparison.subprocess, "run",
                        lambda *a, **k: SimpleNamespace(returncode=0, stderr=b""))
    comparison.compare(args)
    report = json.loads(args.output.read_text())
    assert list(report["results"][0]["implementations"]) == ["local"]
    assert report["sourceSha256"]["local"] == comparison.file_digest(tmp_path / "1.py")


def test_rejects_unreviewed_or_modified_source(tmp_path):
    args = setup_case(tmp_path)
    args.reviewed = [2]
    with pytest.raises(ValueError, match="missing"):
        comparison.compare(args)
    args.reviewed = [1]
    (tmp_path / "1.py").write_text("print(2)\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        comparison.compare(args)


def test_rejects_modified_test_or_duplicate_case(tmp_path):
    args = setup_case(tmp_path)
    args.cases *= 2
    with pytest.raises(ValueError, match="duplicate"):
        comparison.compare(args)
    args.cases = ["example_00"]
    (args.problem / "in" / "example_00.in").write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        comparison.compare(args)


def test_distinct_valid_outputs_use_checker_and_failures_preserve_report(tmp_path, monkeypatch):
    args = setup_case(tmp_path)
    calls = []

    def measure(command, input_path, output_path, rss_path, timeout):
        output_path.write_text(str(len(calls)))
        calls.append(command)
        return 0.25 + len(calls), 1234

    monkeypatch.setattr(comparison, "measure", measure)
    monkeypatch.setattr(comparison.subprocess, "check_output", lambda *a, **k: "version")
    monkeypatch.setattr(comparison.subprocess, "run",
                        lambda *a, **k: SimpleNamespace(returncode=0, stderr=b""))
    comparison.compare(args)
    saved = args.output.read_bytes()
    report = json.loads(saved)
    result = report["results"][0]["implementations"]["1"]
    assert result["medianSeconds"] == 1.75
    assert len({sample["outputSha256"] for sample in result["samples"]}) == 2
    monkeypatch.setattr(comparison.subprocess, "run",
                        lambda *a, **k: SimpleNamespace(returncode=1, stderr=b"wrong answer"))
    with pytest.raises(ValueError, match="wrong answer"):
        comparison.compare(args)
    assert args.output.read_bytes() == saved
