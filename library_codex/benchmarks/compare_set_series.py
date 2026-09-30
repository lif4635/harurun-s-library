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


def run(source, operation, bits, seed):
    spec = importlib.util.spec_from_file_location("candidate", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rng = random.Random(seed)
    size = 1 << bits
    first = [rng.randrange(998244353) for _ in range(size)]
    second = [rng.randrange(998244353) for _ in range(size)]
    first[0] = 0
    engine = module.SubsetConvolution()
    if operation == "multiply":
        function, args = engine.multiply, (first, second)
    elif operation == "exponential":
        function, args = engine.exponential, (first,)
    else:
        function, args = engine.compose_egf, (first, second[:bits + 1])
    start = perf_counter()
    result = function(*args)
    elapsed = perf_counter() - start
    digest = lambda values: hashlib.sha256(json.dumps(values).encode()).hexdigest()
    return dict(seconds=elapsed, rssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                inputSha256=digest(args), outputSha256=digest(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--bits", type=int, default=18)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--operation", choices=("multiply", "exponential", "compose_egf"), default="multiply")
    parser.add_argument("--child", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 0 <= args.bits <= 20 or args.repeat < 1:
        parser.error("invalid bits or repeat")
    if args.child:
        print(json.dumps(run(args.child, args.operation, args.bits, args.seed)))
        return
    if args.output is None:
        parser.error("--output is required")
    sources = dict(baseline=args.baseline.resolve(),
                   current=ROOT / "library_codex/bitwise_convolution/SetFunction.py")
    samples = {name: [] for name in sources}
    for iteration in range(args.repeat):
        for name in (sources if iteration % 2 == 0 else reversed(sources)):
            command = [sys.executable, str(Path(__file__).resolve()), "--baseline", str(args.baseline),
                       "--bits", str(args.bits), "--seed", str(args.seed),
                       "--operation", args.operation, "--child", str(sources[name])]
            sample = json.loads(subprocess.check_output(command, timeout=120))
            samples[name].append(sample)
            print(name, iteration, sample["seconds"], flush=True)
    if len({row["outputSha256"] for rows in samples.values() for row in rows}) != 1:
        raise ValueError("outputs disagree")
    result = dict(bits=args.bits, operation=args.operation, seed=args.seed,
                  python=platform.python_version(), implementation=platform.python_implementation(),
                  timing="function only, fresh sequential process, no warm-up", samples=samples,
                  sourceSha256={name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()},
                  medianSeconds={name: statistics.median(row["seconds"] for row in rows)
                                 for name, rows in samples.items()})
    atomic_write(args.output, json_bytes(result))


if __name__ == "__main__":
    main()
