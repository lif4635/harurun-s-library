import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.benchmarks.official_benchmark import runtime_info
from library_codex.benchmarks.official_comparison import measure
from library_codex.tools.check_library_checker import (
    SUITE, build_solution, case_names, file_digest, load_official, save_json,
)


def selected_generators(problem, names):
    mapping = {
        Path(test["name"]).stem + "_" + str(i).zfill(2): (test["name"], i)
        for test in problem.config["tests"]
        for i in range(test["number"])
    }
    if not names or len(set(names)) != len(names) or any(name not in mapping for name in names):
        raise ValueError("select distinct official case names")
    return [(name, *mapping[name]) for name in names]


def prepare_cases(problem, names):
    spec = importlib.util.spec_from_file_location("official_generator", problem.rootdir / "generate.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    selected = selected_generators(problem, names)
    hashes = json.loads((problem.basedir / "hash.json").read_text())
    problem.generate_params_h()
    problem.compile_correct()
    problem.compile_verifier()
    problem.compile_checker()
    compiled = set()
    for name, source_name, index in selected:
        for folder in ("in", "out"):
            (problem.basedir / folder).mkdir(exist_ok=True)
        input_path = problem.basedir / "in" / (name + ".in")
        expected_path = problem.basedir / "out" / (name + ".out")
        for path in (input_path, expected_path):
            if path.exists() and file_digest(path) != hashes.get(path.name):
                raise ValueError("existing official cache hash mismatch: " + str(path))
        with tempfile.TemporaryDirectory(prefix="harurun-official-probe-") as directory:
            temporary = Path(directory)
            if not input_path.exists():
                source = problem.basedir / "gen" / source_name
                if source_name not in compiled:
                    generator.compile(source, problem.rootdir)
                    compiled.add(source_name)
                candidate = temporary / "input"
                with candidate.open("wb") as output:
                    subprocess.run(generator.execcmd(source, [str(index)]), stdout=output,
                                   check=True, timeout=180)
                if file_digest(candidate) != hashes.get(input_path.name):
                    raise ValueError("generated input hash mismatch: " + name)
                with candidate.open("rb") as data:
                    subprocess.run(generator.execcmd(problem.verifier), stdin=data, check=True, timeout=180)
                shutil.copyfile(candidate, input_path)
            if not expected_path.exists():
                candidate = temporary / "expected"
                with input_path.open("rb") as data, candidate.open("wb") as output:
                    subprocess.run(generator.execcmd(problem.basedir / "sol/correct.cpp"),
                                   stdin=data, stdout=output, check=True, timeout=300)
                if file_digest(candidate) != hashes.get(expected_path.name):
                    raise ValueError("generated answer hash mismatch: " + name)
                shutil.copyfile(candidate, expected_path)
        print("prepared " + name, flush=True)


def probe(args):
    if args.repeat < 1 or (args.timeout is not None and args.timeout <= 0):
        raise ValueError("repeat and timeout must be positive")
    problem = load_official(args.official)[args.problem]
    selected_generators(problem, args.cases)
    environment = runtime_info(args.python)
    script, modules = build_solution(args.problem)
    prepare_cases(problem, args.cases)
    limit = float(problem.config["timelimit"])
    timeout = args.timeout or limit
    checker = problem.checker.with_suffix("")
    report = dict(
        schemaVersion=1, kind="selected-official-case-probe", problem=args.problem,
        measuredAt=datetime.now(timezone.utc).isoformat(), environment=environment,
        sourceSha256=file_digest(script), modules=modules, problemVersion=problem.problem_version(),
        upstreamRevision=subprocess.check_output(
            ["git", "-C", str(problem.rootdir), "rev-parse", "HEAD"], text=True).strip(),
        officialCases=len(case_names(problem)), selectedCases=args.cases,
        timeLimitSeconds=limit, timeoutSeconds=timeout, repeat=args.repeat,
        checkerSha256=file_digest(checker), officialHashSha256=file_digest(problem.basedir / "hash.json"),
        status="incomplete", onlineSubmission=None, results=[],
        protocol="selected official hash-verified cases only; sequential fresh PyPy processes; startup, JIT and I/O included; official checker; GNU time RSS; no memory limit enforcement; does not update full verification",
    )
    output = args.output or SUITE / "benchmarks/comparisons" / (args.problem + "-probe.json")
    save_json(output, report)
    with tempfile.TemporaryDirectory(prefix="harurun-probe-") as directory:
        temporary = Path(directory)
        isolated = temporary / "main.py"
        isolated.write_bytes(script.read_bytes())
        for iteration in range(args.repeat):
            names = args.cases[:]
            random.Random(92471 + iteration).shuffle(names)
            for name in names:
                input_path = problem.basedir / "in" / (name + ".in")
                expected_path = problem.basedir / "out" / (name + ".out")
                actual = temporary / "actual"
                row = dict(case=name, iteration=iteration + 1,
                           inputSha256=file_digest(input_path), expectedSha256=file_digest(expected_path))
                stage = "solution"
                try:
                    seconds, rss = measure([args.python, str(isolated)], input_path, actual,
                                           temporary / "rss", timeout)
                    stage = "checker"
                    checked = subprocess.run([str(checker), str(input_path), str(actual), str(expected_path)],
                                             capture_output=True, timeout=180)
                    row.update(seconds=seconds, peakRssKiB=rss, outputSha256=file_digest(actual),
                               status="AC" if checked.returncode == 0 else
                               "WA" if checked.returncode in (1, 2) else "CHECKER_ERROR",
                               withinOfficialTimeLimit=seconds <= limit)
                    if checked.returncode:
                        row["diagnostic"] = checked.stderr.decode(errors="replace")[-2000:]
                except subprocess.TimeoutExpired:
                    row.update(status="TLE" if stage == "solution" else "CHECKER_ERROR",
                               timeoutSeconds=timeout if stage == "solution" else 180,
                               withinOfficialTimeLimit=False)
                except RuntimeError as error:
                    row.update(status="RE", diagnostic=str(error)[-2000:])
                report["results"].append(row)
                save_json(output, report)
                print(json.dumps(row), flush=True)
    report["status"] = "selected_cases_passed" if all(
        row["status"] == "AC" and row["withinOfficialTimeLimit"] for row in report["results"]
    ) else "selected_cases_failed"
    save_json(output, report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--output", type=Path)
    if probe(parser.parse_args())["status"] != "selected_cases_passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
