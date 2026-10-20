import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from math import isqrt
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_codex.benchmarks.official_benchmark import runtime_info
from library_codex.benchmarks.official_comparison import measure
from library_codex.number_theory.MultiplicativeFunctions import MultiplicativePrefixSum
from library_codex.prime.Sieve import prime_sieve
from library_codex.tools.check_library_checker import file_digest, save_json


def baseline(revision):
    source = subprocess.check_output(
        ["git", "-c", "safe.directory=*", "show", revision + ":library_codex/number_theory/MultiplicativeFunctions.py"],
        cwd=ROOT, text=True,
    )
    cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "MultiplicativePrefixSum")
    namespace = dict(isqrt=isqrt, prime_sieve=prime_sieve)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), "baseline", "exec"), namespace)
    return namespace["MultiplicativePrefixSum"], hashlib.sha256(source.encode()).hexdigest()


def worker(mode, revision):
    old, source_hash = baseline(revision)
    cls = old if mode == "baseline" else MultiplicativePrefixSum
    read = sys.stdin.buffer.readline
    phases, answers = [], []
    mod = 469762049
    for _ in range(int(read())):
        n, a, b = map(int, read().split())
        start = perf_counter()
        engine = cls(n, mod)
        constructed = perf_counter()
        counts = engine.prime_count_table() if a else [0] * engine.size
        counted = perf_counter()
        sums = engine.prime_sum_table() if b else [0] * engine.size
        summed = perf_counter()
        prefix = [(a * x + b * y) % mod for x, y in zip(counts, sums)]
        combined = perf_counter()
        answers.append(engine.run(prefix, lambda p, e: (a * e + b * p) % mod))
        phases.append(dict(n=n, constructor=constructed-start, counts=counted-constructed,
                           sums=summed-counted, prefix=combined-summed, run=perf_counter()-combined))
    print(json.dumps(dict(answers=answers, phases=phases, baselineSourceSha256=source_hash)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path)
    parser.add_argument("--revision", default="23457b9c61f00cd404df9fc1a1c95ebaacbb92d5")
    parser.add_argument("--cases", nargs="+", default=["max_00"])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--worker", choices=["baseline", "current"])
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/multiplicative_sum_large.json")
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.revision)
        return
    if args.official is None or args.repeat < 1 or args.timeout <= 0:
        parser.error("official path, positive repeat and timeout are required")
    problem = args.official / "number_theory/sum_of_multiplicative_function_large"
    hashes = json.loads((problem / "hash.json").read_text())
    report = dict(schemaVersion=1, measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=runtime_info(sys.executable), baselineRevision=args.revision,
                  sourceSha256=file_digest(ROOT / "library_codex/number_theory/MultiplicativeFunctions.py"),
                  checkerSha256=file_digest(problem / "checker"), officialHashSha256=file_digest(problem / "hash.json"),
                  repeat=args.repeat, timeLimitSeconds=30, measurementTimeoutSeconds=args.timeout,
                  protocol="sequential fresh PyPy processes; shuffled order; official checker; wall time includes startup, baseline extraction, JIT and I/O; memory limit not enforced; extended measurement timeout is not an AC result",
                  results=[])
    jobs = [(case, mode) for case in args.cases for mode in ("baseline", "current") for _ in range(args.repeat)]
    random.Random(281731).shuffle(jobs)
    with tempfile.TemporaryDirectory(prefix="harurun-multiplicative-") as directory:
        temporary = Path(directory)
        for case, mode in jobs:
            if Path(case).name != case:
                raise ValueError("invalid case name")
            inp, expected = problem / "in" / (case + ".in"), problem / "out" / (case + ".out")
            for path in (inp, expected):
                if file_digest(path) != hashes.get(path.name):
                    raise ValueError("official test hash mismatch")
            output = temporary / "worker.json"
            elapsed, rss = measure([sys.executable, __file__, "--worker", mode, "--revision", args.revision],
                                   inp, output, temporary / "rss.txt", args.timeout)
            row = json.loads(output.read_text())
            actual = temporary / "actual.out"
            actual.write_text("\n".join(map(str, row.pop("answers"))) + "\n")
            subprocess.run([str(problem / "checker"), str(inp), str(actual), str(expected)],
                           check=True, capture_output=True, timeout=30)
            row.update(case=case, mode=mode, seconds=elapsed, peakRssKiB=rss, checkerPassed=True,
                       withinTimeLimit=elapsed <= 30, inputSha256=file_digest(inp), outputSha256=file_digest(actual))
            report["results"].append(row)
            save_json(args.output, report)
            print(json.dumps(row), flush=True)
    report["summary"] = [dict(case=case, mode=mode,
        medianSeconds=statistics.median(r["seconds"] for r in report["results"] if r["case"] == case and r["mode"] == mode),
        peakRssKiB=max(r["peakRssKiB"] for r in report["results"] if r["case"] == case and r["mode"] == mode))
        for case in args.cases for mode in ("baseline", "current")]
    save_json(args.output, report)
    print(json.dumps(report["summary"]), flush=True)


if __name__ == "__main__":
    main()
