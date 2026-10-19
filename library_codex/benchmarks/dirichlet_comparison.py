import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_codex.number_theory import MultiplicativeFunctions as current
from library_codex.tools.build_codon import atomic_write


def measure(n, operation, mode, revision):
    source = subprocess.check_output(
        ["git", "-c", "safe.directory=*", "show", revision + ":library_codex/number_theory/MultiplicativeFunctions.py"],
        cwd=ROOT, text=True,
    )
    old = {}
    exec(compile(source, "baseline", "exec"), old)
    first = current.DirichletQuotientSeries(n, mod=998244353)
    second = current.DirichletQuotientSeries(n, mod=998244353)
    rng = random.Random(32178)
    first.data = [0, 1] + [rng.randrange(first.mod) for _ in range(first.size - 2)]
    second.data = [0] + [rng.randrange(first.mod) for _ in range(first.size - 1)]
    function = old[operation] if mode == "baseline" else getattr(current, operation)
    start = perf_counter()
    result = function(second, first).data
    elapsed = perf_counter() - start
    checksum = hashlib.sha256(json.dumps(result).encode()).hexdigest()
    return dict(n=n, operation=operation, mode=mode, seconds=elapsed,
                resultSha256=checksum, baselineSourceSha256=hashlib.sha256(source.encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="1c37897b35ed108a1dd406ebd2c994a53dcafdf8")
    parser.add_argument("--sizes", type=int, nargs="+", default=[10**10, 10**12])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--operation", choices=["dirichlet_multiply", "dirichlet_divide"])
    parser.add_argument("--worker", choices=["baseline", "current"])
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/dirichlet.json")
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(args.sizes[0], args.operation, args.worker, args.revision)))
        return
    if "PyPy" not in sys.version:
        raise ValueError("run this comparison with PyPy")
    if args.repeat < 1 or args.timeout <= 0:
        raise ValueError("repeat and timeout must be positive")
    operations = [args.operation] if args.operation else ["dirichlet_multiply", "dirichlet_divide"]
    jobs = [(n, op, mode) for n in args.sizes for op in operations for mode in ("baseline", "current") for _ in range(args.repeat)]
    random.Random(89311).shuffle(jobs)
    rows = []
    timed_out = set()
    result = dict(runtime=sys.version, baselineRevision=args.revision,
                  sourceSha256=hashlib.sha256((ROOT / "library_codex/number_theory/MultiplicativeFunctions.py").read_bytes()).hexdigest(),
                  scope="operation only; seeded quotient prefix tables prepared before timing; fresh process; same inputs; modulo 998244353",
                  timeoutScope="whole worker including input preparation; stop repeating a timed-out configuration",
                  repeat=args.repeat, timeoutSeconds=args.timeout, complete=False, runs=rows)
    for n, op, mode in jobs:
        if (n, op, mode) in timed_out:
            continue
        try:
            output = subprocess.check_output([sys.executable, __file__, "--worker", mode, "--operation", op, "--sizes", str(n), "--revision", args.revision], timeout=args.timeout, text=True)
            row = json.loads(output)
            row["outcome"] = "completed"
        except subprocess.TimeoutExpired:
            timed_out.add((n, op, mode))
            row = dict(n=n, operation=op, mode=mode, outcome="timeout", timeoutSeconds=args.timeout)
        rows.append(row)
        atomic_write(args.output, json.dumps(result, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    summary = []
    for n in args.sizes:
        for op in operations:
            finished = [r for r in rows if r["n"] == n and r["operation"] == op and r["outcome"] == "completed"]
            assert len({r["resultSha256"] for r in finished}) <= 1
            for mode in ("baseline", "current"):
                seconds = [r["seconds"] for r in finished if r["mode"] == mode]
                summary.append(dict(n=n, operation=op, mode=mode,
                                    medianSeconds=statistics.median(seconds) if seconds else None,
                                    completedRuns=len(seconds), timedOut=(n, op, mode) in timed_out,
                                    crossImplementationCompared={r["mode"] for r in finished} == {"baseline", "current"}))
    result.update(complete=True, summary=summary)
    atomic_write(args.output, json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
