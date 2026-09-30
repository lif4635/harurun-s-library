import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from library_codex.benchmarks.library_checker import atomic_write, json_bytes


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(args, mode):
    if mode == "baseline":
        module = load(args.baseline, "baseline_fps")
        old = load(args.baseline_multiply, "baseline_multiply")
        if args.baseline_ntt:
            old._multiply998 = load(args.baseline_ntt, "baseline_ntt").multiply
        module.multivariate_multiplication = old.multivariate_multiplication
        module._multiply_prefix = old._multiply_prefix
    else:
        module = load(ROOT / "library_codex/fps/MultivariateFPS.py", "candidate_fps")
    rng = random.Random(args.seed)
    size = args.width * args.height
    values = [rng.randrange(998244353) for _ in range(size)] if args.family == "dense" else [0] * size
    if args.family != "dense":
        positions = (sorted(range(1, size), key=lambda i: (i % args.width + i // args.width, i))[:args.terms]
                     if args.family == "sparse-low" else rng.sample(range(1, size), min(args.terms, size - 1)))
        for index in positions:
            values[index] = rng.randrange(998244353)
    values[0] = 0 if args.operation == "exponential" else 1
    series = module.MultivariateFormalPowerSeries(values, (args.width, args.height))
    function = getattr(series, args.operation)
    start = perf_counter()
    result = function(1234567) if args.operation == "power" else function()
    elapsed = perf_counter() - start
    digest = lambda data: hashlib.sha256(json.dumps(data).encode()).hexdigest()
    rss = next(int(line.split()[1]) for line in Path("/proc/self/status").read_text().splitlines() if line.startswith("VmHWM:"))
    return dict(seconds=elapsed, rssKiB=rss,
                inputSha256=digest(values), outputSha256=digest(result.coefficients))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--baseline-multiply", type=Path, required=True)
    parser.add_argument("--baseline-ntt", type=Path)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--operation", choices=("inverse", "logarithm", "exponential", "power"), default="inverse")
    parser.add_argument("--family", choices=("dense", "sparse", "sparse-low"), default="dense")
    parser.add_argument("--terms", type=int, default=8)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--child", choices=("baseline", "current"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.width < 1 or args.height < 1 or args.repeat < 1 or args.terms < 0:
        parser.error("shape and repeat must be positive")
    if args.child:
        print(json.dumps(run(args, args.child)))
        return
    if args.output is None:
        parser.error("--output is required")
    samples = dict(baseline=[], current=[])
    timed_out = set()
    for iteration in range(args.repeat):
        for mode in (("baseline", "current") if iteration % 2 == 0 else ("current", "baseline")):
            if mode in timed_out:
                continue
            command = [sys.executable, str(Path(__file__).resolve()), "--baseline", str(args.baseline),
                       "--baseline-multiply", str(args.baseline_multiply), "--width", str(args.width),
                       "--height", str(args.height), "--seed", str(args.seed), "--operation", args.operation,
                       "--family", args.family, "--child", mode]
            command.extend(["--terms", str(args.terms)])
            if args.baseline_ntt:
                command.extend(["--baseline-ntt", str(args.baseline_ntt)])
            try:
                sample = json.loads(subprocess.check_output(command, timeout=args.timeout))
            except subprocess.TimeoutExpired:
                timed_out.add(mode)
                print(mode, "timed out", flush=True)
                continue
            samples[mode].append(sample)
            print(mode, iteration, sample["seconds"], flush=True)
    if len({row["outputSha256"] for rows in samples.values() for row in rows}) > 1:
        raise ValueError("outputs disagree")
    sources = dict(baseline=args.baseline, baselineMultiply=args.baseline_multiply,
                   current=ROOT / "library_codex/fps/MultivariateFPS.py",
                  currentMultiply=ROOT / "library_codex/convolution/MultivariateMultiplication.py",
                  currentNtt=ROOT / "library_codex/convolution/NTT998.py")
    if args.baseline_ntt:
        sources["baselineNtt"] = args.baseline_ntt
    result = dict(shape=[args.width, args.height], family=args.family, terms=args.terms, operation=args.operation,
                  memoryMetric="/proc/self/status VmHWM after calculation",
                  seed=args.seed, timing="function only, fresh sequential process, no warm-up",
                  implementation=platform.python_implementation(), python=platform.python_version(),
                  timeoutSeconds=args.timeout, timedOut=sorted(timed_out), samples=samples,
                  sourceSha256={name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()},
                  medianSeconds={name: statistics.median(row["seconds"] for row in rows)
                                 for name, rows in samples.items() if rows})
    atomic_write(args.output, json_bytes(result))


if __name__ == "__main__":
    main()
