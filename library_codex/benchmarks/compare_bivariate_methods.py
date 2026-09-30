import argparse
import hashlib
import importlib
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
from library_codex.benchmarks.bivariate_candidates import colored_inverse, row_inverse, sparse_unlimited


def coefficients(width, height, operation, family, count, seed):
    rng = random.Random(seed)
    size = width * height
    if family == "dense":
        values = [rng.randrange(998244353) for _ in range(size)]
    else:
        values = [0] * size
        if family == "sparse-low":
            positions = sorted(range(1, size), key=lambda i: (i % width + i // width, i))
            positions = positions[:count]
        else:
            positions = rng.sample(range(1, size), min(count, size - 1))
        for i in positions:
            values[i] = rng.randrange(1, 998244353)
    values[0] = 0 if operation == "exponential" else 1
    return values


def digest(values):
    return hashlib.sha256(" ".join(map(str, values)).encode()).hexdigest()


def peak_rss():
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmHWM:"):
            return int(line.split()[1])
    raise RuntimeError("VmHWM unavailable")


def run_python(args):
    fields = sys.stdin.buffer.read().split()
    width, height = map(int, fields[:2])
    operation = fields[2].decode()
    exponent = int(fields[3])
    values = list(map(int, fields[4:]))
    if len(values) != width * height:
        raise ValueError("invalid input length")
    module = importlib.import_module("library_codex.fps.MultivariateFPS")
    if args.child != "current":
        module._sparse_2d = sparse_unlimited if args.child == "sparse" else lambda *a, **k: None
    if args.child == "colored":
        module._inverse_prefix = colored_inverse
    if args.child == "row":
        module._inverse_prefix = row_inverse
    source = module.MultivariateFormalPowerSeries(values, (width, height))
    function = getattr(source, operation)
    arguments = (exponent,) if operation == "power" else ()
    for _ in range(args.warmups):
        function(*arguments)
    start = perf_counter()
    result = function(*arguments).coefficients
    seconds = perf_counter() - start
    rss = peak_rss()
    inherited = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(dict(seconds=seconds, rssKiB=rss, rusageMaxRssKiB=inherited, outputSha256=digest(result))))


def compare(args):
    binaries = {name: path for name, path in (("maspy", args.maspy), ("nyaan", args.nyaan)) if path}
    if any(mode in ("maspy", "nyaan") and mode not in binaries for mode in args.modes):
        raise ValueError("C++ mode needs its compiled executable")
    cases = []
    for shape in args.shapes:
        width, height = map(int, shape.split("x"))
        if min(width, height) < 1:
            raise ValueError("positive shape required")
        for operation in args.operations:
            for family in args.families:
                for count in ([0] if family == "dense" else args.terms):
                    values = coefficients(width, height, operation, family, count, args.seed)
                    payload = f"{width} {height} {operation} {args.exponent}\n" + " ".join(map(str, values)) + "\n"
                    samples = {mode: [] for mode in args.modes}
                    skipped = {}
                    for iteration in range(args.repeat):
                        order = args.modes[iteration % len(args.modes):] + args.modes[:iteration % len(args.modes)]
                        for mode in order:
                            if mode in skipped:
                                continue
                            if mode == "sparse" and family == "dense":
                                skipped[mode] = "not run on dense input"
                                continue
                            command = ([str(binaries[mode]), str(args.warmups)] if mode in binaries else
                                       [sys.executable, str(Path(__file__).resolve()), "--child", mode, "--warmups", str(args.warmups)])
                            try:
                                start = perf_counter()
                                completed = subprocess.run(command, input=payload.encode(), capture_output=True, timeout=args.timeout, check=True)
                                wall = perf_counter() - start
                            except subprocess.TimeoutExpired:
                                skipped[mode] = f"timeout {args.timeout}s"
                                continue
                            if mode in binaries:
                                seconds, rss, inherited = completed.stderr.split()
                                sample = dict(seconds=float(seconds), rssKiB=int(rss), rusageMaxRssKiB=int(inherited),
                                              outputSha256=digest(list(map(int, completed.stdout.split()))))
                            else:
                                sample = json.loads(completed.stdout)
                            sample["wallSeconds"] = wall
                            samples[mode].append(sample)
                            if len({s["outputSha256"] for rows in samples.values() for s in rows}) != 1:
                                raise ValueError(f"output mismatch: {shape} {operation} {family} {count} {mode}")
                    result = dict(shape=[width, height], operation=operation, family=family, terms=count,
                                  inputSha256=hashlib.sha256(payload.encode()).hexdigest(), samples=samples, skipped=skipped,
                                  medianSeconds={mode: statistics.median(s["seconds"] for s in rows) for mode, rows in samples.items() if rows},
                                  maxRssKiB={mode: max(s["rssKiB"] for s in rows) for mode, rows in samples.items() if rows})
                    cases.append(result)
                    print(shape, operation, family, count, result["medianSeconds"], skipped, flush=True)
                    files = [Path(__file__), ROOT / "library_codex/benchmarks/bivariate_candidates.py",
                             ROOT / "library_codex/fps/MultivariateFPS.py", ROOT / "library_codex/convolution/NTT998.py",
                             ROOT / "library_codex/convolution/MultivariateMultiplication.py",
                             ROOT / "library_codex/benchmarks/bivariate_reference.cpp"]
                    report = dict(cases=cases, seed=args.seed, exponent=args.exponent, repeat=args.repeat,
                                  warmups=args.warmups, python=platform.python_version(),
                                  implementation=platform.python_implementation(),
                                  memoryMetric="/proc/self/status VmHWM after calculation; excludes inherited pre-exec high-water mark",
                                  timing="function only; fresh sequential processes; wallSeconds also includes startup and input/output",
                                  sourceSha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                                  binaries={name: dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for name, path in binaries.items()},
                                  references=dict(maspy="ede5df59c235e19937893bff5fc59c6f94aa06d4",
                                                  nyaan="b3981adc80a800b2584980b01821324ea6c77183"))
                    atomic_write(args.output, json_bytes(report))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=("current", "packed", "colored", "row", "sparse"))
    parser.add_argument("--shapes", nargs="+", default=["256x256"])
    parser.add_argument("--operations", nargs="+", default=["inverse"], choices=("inverse", "logarithm", "exponential", "power"))
    parser.add_argument("--families", nargs="+", default=["dense"], choices=("dense", "sparse-low", "sparse-random"))
    parser.add_argument("--terms", nargs="+", type=int, default=[8, 16, 17, 32, 64])
    parser.add_argument("--modes", nargs="+", default=["current", "colored", "row"], choices=("current", "packed", "colored", "row", "sparse", "maspy", "nyaan"))
    parser.add_argument("--exponent", type=int, default=1234567)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--maspy", type=Path)
    parser.add_argument("--nyaan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeat < 1 or args.warmups < 0 or any(k < 0 for k in args.terms):
        parser.error("invalid repeat, warmups or terms")
    if args.child:
        run_python(args)
    elif args.output is None:
        parser.error("--output is required")
    else:
        compare(args)


if __name__ == "__main__":
    main()
