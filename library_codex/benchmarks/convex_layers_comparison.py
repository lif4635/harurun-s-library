import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_codex.geometry.ConvexLayers import onion_depth
from library_codex.tools.build_codon import atomic_write


def measure(n, shape, mode, revision):
    source = subprocess.check_output(
        ["git", "-c", "safe.directory=*", "show", revision + ":library_codex/geometry/ConvexLayers.py"],
        cwd=ROOT, text=True,
    )
    baseline = {}
    exec(compile(source, "baseline", "exec"), baseline)
    rng = random.Random(89172)
    if shape == "nested":
        points = [(sx * r, sy * r) for r in range(1, n // 4 + 1) for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1))]
    else:
        points = [(rng.randrange(10**6), rng.randrange(10**6)) for _ in range(n)]
    rng.shuffle(points)
    input_hash = hashlib.sha256(repr(points).encode()).hexdigest()
    function = baseline["onion_depth"] if mode == "baseline" else onion_depth
    start = perf_counter()
    result = function(points)
    elapsed = perf_counter() - start
    if shape == "nested":
        assert result == [n // 4 - abs(x) for x, y in points]
    return dict(n=len(points), shape=shape, mode=mode, seconds=elapsed,
                peakRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                inputSha256=input_hash, resultSha256=hashlib.sha256(repr(result).encode()).hexdigest(),
                baselineSourceSha256=hashlib.sha256(source.encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="990aeb542ddddb34f2f77b87325ff82aaa533c77")
    parser.add_argument("--size", type=int, default=20000)
    parser.add_argument("--shape", choices=["nested", "random"])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--worker", choices=["baseline", "current"])
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/convex_layers.json")
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(args.size, args.shape, args.worker, args.revision)))
        return
    if "PyPy" not in sys.version or args.size < 4 or args.repeat < 1 or args.timeout <= 0:
        raise ValueError("use PyPy, size >= 4, positive repeat and timeout")
    shapes = [args.shape] if args.shape else ["nested", "random"]
    jobs = [(shape, mode) for shape in shapes for mode in ("baseline", "current") for _ in range(args.repeat)]
    random.Random(78923).shuffle(jobs)
    rows, timed_out = [], set()
    report = dict(runtime=sys.version, baselineRevision=args.revision,
                  sourceSha256=hashlib.sha256((ROOT / "library_codex/geometry/ConvexLayers.py").read_bytes()).hexdigest(),
                  scope="onion_depth operation only; same seeded points; fresh processes; RSS includes interpreter and input preparation",
                  timeoutScope="whole worker; stop repeating a timed-out configuration",
                  repeat=args.repeat, timeoutSeconds=args.timeout, complete=False, runs=rows)
    for shape, mode in jobs:
        if (shape, mode) in timed_out:
            continue
        try:
            output = subprocess.check_output([sys.executable, __file__, "--worker", mode, "--shape", shape,
                                              "--size", str(args.size), "--revision", args.revision],
                                             timeout=args.timeout, text=True)
            row = json.loads(output)
            row["outcome"] = "completed"
        except subprocess.TimeoutExpired:
            timed_out.add((shape, mode))
            row = dict(n=args.size, shape=shape, mode=mode, outcome="timeout", timeoutSeconds=args.timeout)
        rows.append(row)
        atomic_write(args.output, json.dumps(report, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    summary = []
    for shape in shapes:
        finished = [r for r in rows if r["shape"] == shape and r["outcome"] == "completed"]
        assert len({(r["inputSha256"], r["resultSha256"]) for r in finished}) <= 1
        for mode in ("baseline", "current"):
            values = [r["seconds"] for r in finished if r["mode"] == mode]
            summary.append(dict(shape=shape, mode=mode, medianSeconds=statistics.median(values) if values else None,
                                completedRuns=len(values), timedOut=(shape, mode) in timed_out,
                                crossImplementationCompared={r["mode"] for r in finished} == {"baseline", "current"}))
    report.update(complete=True, summary=summary)
    atomic_write(args.output, json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
