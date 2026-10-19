import argparse
import ast
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

from library_codex.number_theory.MultiplicativeFunctions import MultiplicativePrefixSum
from library_codex.tools.build_codon import atomic_write


def baseline(revision):
    source = subprocess.check_output(
        ["git", "-c", "safe.directory=*", "show", revision + ":library_codex/number_theory/MultiplicativeFunctions.py"],
        cwd=ROOT, text=True,
    )
    cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "MultiplicativePrefixSum")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "run")
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), "baseline", "exec"), namespace)
    return namespace["run"], hashlib.sha256(source.encode()).hexdigest()


def measure(n, mode, revision):
    old, source_hash = baseline(revision)
    engine = MultiplicativePrefixSum(n, 469762049)
    prefix = [(123 * x + 456 * y) % 469762049 for x, y in zip(engine.prime_count_table(), engine.prime_sum_table())]
    start = perf_counter()
    run = old if mode == "baseline" else MultiplicativePrefixSum.run
    result = run(engine, prefix, lambda p, e: (123 * e + 456 * p) % 469762049)
    return dict(n=n, mode=mode, seconds=perf_counter() - start, result=result, baselineSourceSha256=source_hash)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="ccc0335adba8522f9f66e0a351a6a5e1cd9d7c54")
    parser.add_argument("--sizes", type=int, nargs="+", default=[10**8, 10**9])
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--worker", choices=["baseline", "current"])
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/multiplicative_sum.json")
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(args.sizes[0], args.worker, args.revision)))
        return
    if "PyPy" not in sys.version:
        raise ValueError("run this comparison with PyPy")
    jobs = [(n, mode) for n in args.sizes for mode in ("baseline", "current") for _ in range(args.repeat)]
    random.Random(47281).shuffle(jobs)
    rows = []
    for n, mode in jobs:
        output = subprocess.check_output([sys.executable, __file__, "--worker", mode, "--sizes", str(n), "--revision", args.revision], timeout=60, text=True)
        row = json.loads(output)
        rows.append(row)
        print(json.dumps(row), flush=True)
    for n in args.sizes:
        assert len({row["result"] for row in rows if row["n"] == n}) == 1
    summary = [{"n": n, "mode": mode, "medianSeconds": statistics.median(row["seconds"] for row in rows if row["n"] == n and row["mode"] == mode)} for n in args.sizes for mode in ("baseline", "current")]
    result = dict(runtime=sys.version, baselineRevision=args.revision, sourceSha256=hashlib.sha256((ROOT / "library_codex/number_theory/MultiplicativeFunctions.py").read_bytes()).hexdigest(), scope="run only; tables prepared before timing; fresh process; same input and callback", repeat=args.repeat, runs=rows, summary=summary)
    atomic_write(args.output, json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
