import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_codex.benchmarks.library_checker import atomic_write, json_bytes


def run(source, operation, size, count, seed):
    spec = importlib.util.spec_from_file_location("candidate", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rng = random.Random(seed)
    series = [0] * size
    series[0] = 0 if operation == "exponential" else 1
    positions = [1] + rng.sample(range(2, size), count - 1)
    for position in positions:
        series[position] = rng.randrange(1, 998244353)
    name = "sparse_" + operation
    if not hasattr(module, name):
        name = {"power": "fps_pow", "exponential": "fps_exp", "logarithm": "fps_log"}[operation]
    function = getattr(module, name)
    args = (series, 1234567, size) if operation == "power" else (series, size)
    start = perf_counter()
    result = function(*args)
    elapsed = perf_counter() - start
    digest = lambda values: hashlib.sha256(json.dumps(values).encode()).hexdigest()
    return dict(seconds=elapsed, rssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                inputSha256=digest(series), outputSha256=digest(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, default=ROOT / "library_codex/fps/SparseFormalPowerSeries.py")
    parser.add_argument("--size", type=int, default=131072)
    parser.add_argument("--terms", type=int, default=8)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--operation", choices=("power", "exponential", "logarithm"), default="power")
    parser.add_argument("--child", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.terms < args.size or args.repeat < 1:
        parser.error("require 1 <= terms < size and repeat >= 1")
    if args.child:
        print(json.dumps(run(args.child, args.operation, args.size, args.terms, args.seed)))
        return
    if args.output is None:
        parser.error("--output is required")
    sources = dict(baseline=args.baseline.resolve(), current=args.candidate.resolve())
    samples = {name: [] for name in sources}
    timed_out = set()
    for iteration in range(args.repeat):
        for name in (sources if iteration % 2 == 0 else reversed(sources)):
            if name in timed_out:
                continue
            command = [sys.executable, str(Path(__file__).resolve()), "--baseline", str(args.baseline),
                       "--size", str(args.size), "--terms", str(args.terms), "--seed", str(args.seed),
                       "--operation", args.operation, "--child", str(sources[name])]
            try:
                sample = json.loads(subprocess.check_output(command, timeout=args.timeout))
            except subprocess.TimeoutExpired:
                timed_out.add(name)
                print(name, "timed out", flush=True)
                continue
            samples[name].append(sample)
            print(name, iteration, sample["seconds"], flush=True)
    outputs = {sample["outputSha256"] for rows in samples.values() for sample in rows}
    if len(outputs) > 1:
        raise ValueError("outputs disagree")
    result = dict(size=args.size, terms=args.terms, operation=args.operation, seed=args.seed,
                  python=platform.python_version(), implementation=platform.python_implementation(),
                  timing="function only, fresh sequential process, no warm-up", timeoutSeconds=args.timeout,
                  timedOut=sorted(timed_out), samples=samples,
                  sourceSha256={name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()},
                  medianSeconds={name: statistics.median(row["seconds"] for row in rows)
                                 for name, rows in samples.items() if rows})
    atomic_write(args.output, json_bytes(result))


if __name__ == "__main__":
    main()
