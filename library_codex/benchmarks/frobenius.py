import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_codex.linear_algebra.Frobenius import Frobenius
from library_codex.linear_algebra.Matrix import matrix_power


CASES = {
    "dense16": (16, "dense", [10**18 + 37]),
    "dense64": (64, "dense", [10**18 + 37]),
    "dense128": (128, "dense", [10**18 + 37]),
    "dense256": (256, "dense", [10**18 + 37]),
    "small-exponent": (128, "dense", [3]),
    "permutation": (128, "permutation", [10**18 + 37]),
    "scalar": (128, "scalar", [10**18 + 37]),
    "jordan": (128, "jordan", [10**18 + 37]),
    "repeated": (128, "dense", [10**18 + 37, 10**18 + 77, 10**18 + 137]),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def worker(case, variant):
    n, shape, exponents = CASES[case]
    mod, rng = 998244353, random.Random(721)
    if shape == "dense":
        matrix = [[rng.randrange(mod) for _ in range(n)] for _ in range(n)]
    elif shape == "permutation":
        permutation = list(range(n))
        rng.shuffle(permutation)
        matrix = [[int(j == permutation[i]) for j in range(n)] for i in range(n)]
    elif shape == "scalar":
        matrix = [[3 * int(i == j) for j in range(n)] for i in range(n)]
    else:
        matrix = [[int(i == j) + int(i == j + 1 and i % 32 != 0) for j in range(n)] for i in range(n)]
    started = perf_counter()
    form = Frobenius(matrix, mod, seed=11) if variant == "frobenius" else None
    built = perf_counter()
    results = [form.pow(k) if form is not None else matrix_power(matrix, k, mod) for k in exponents]
    finished = perf_counter()
    print(json.dumps(dict(seconds=finished-started, buildSeconds=built-started, querySeconds=finished-built,
                         inputSha256=digest([matrix, exponents, mod]), resultSha256=digest(results),
                         blocks=[len(block) for block in form._blocks] if form is not None else None)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/frobenius.json")
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        return
    version = subprocess.check_output([args.python, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("PyPy required")
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        rss = Path(directory) / "rss"
        for case in args.cases or CASES:
            samples, expected = {"binary": [], "frobenius": []}, None
            for iteration in range(args.repeat):
                order = list(samples)
                random.Random(iteration + 77).shuffle(order)
                for variant in order:
                    start = perf_counter()
                    run = subprocess.run(["/usr/bin/time", "-f", "%M", "-o", str(rss), args.python, str(Path(__file__).resolve()), "--worker", case, variant], capture_output=True, text=True, check=True, timeout=180)
                    sample = json.loads(run.stdout)
                    sample.update(wallSeconds=perf_counter() - start, peakRssKiB=int(rss.read_text().strip()))
                    current = sample["inputSha256"], sample["resultSha256"]
                    if expected is None:
                        expected = current
                    assert current == expected, case
                    samples[variant].append(sample)
                    print(case, variant, iteration + 1, round(sample["seconds"], 6), flush=True)
            rows.append(dict(case=case, parameters=CASES[case], samples=samples,
                             summary={key: dict(medianSeconds=statistics.median(s["seconds"] for s in values),
                                                medianBuildSeconds=statistics.median(s["buildSeconds"] for s in values),
                                                medianQuerySeconds=statistics.median(s["querySeconds"] for s in values),
                                                peakRssKiB=max(s["peakRssKiB"] for s in values)) for key, values in samples.items()}))
    paths = ["linear_algebra/Frobenius.py", "linear_algebra/Matrix.py", "benchmarks/frobenius.py"]
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), environment=dict(runtime=version, platform=platform.platform(),
                  cpuInfo=Path("/proc/cpuinfo").read_text().split("model name", 1)[1].splitlines()[0].lstrip("\t: "), affinity=sorted(os.sched_getaffinity(0))),
                  repeat=args.repeat, protocol="fresh sequential PyPy processes; shuffled order; matching input/output hashes; construction included; core and wall time; GNU time RSS; CPU not isolated",
                  sourceSha256={p: hashlib.sha256((ROOT / "library_codex" / p).read_bytes()).hexdigest() for p in paths}, results=rows)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    json.loads(temporary.read_text())
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
