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
from library_codex.linear_algebra.Matrix import matrix_power, matrix_multiply, matrix_vector_multiply


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

OPERATIONS = {
    "vector128": (128, "dense", "pow", 10**18 + 37, 1),
    "vector256": (256, "dense", "pow", 10**18 + 37, 1),
    "vector-small": (128, "dense", "pow", 3, 1),
    "vector-permutation": (128, "permutation", "pow", 10**18 + 37, 1),
    "vector-repeated": (128, "dense", "pow", 10**18 + 37, 5),
    "sum128": (128, "dense", "sum_matrix", 10**18 + 37, 1),
    "sum-vector128": (128, "dense", "sum", 10**18 + 37, 1),
    "sum-identity": (128, "identity", "sum", 10**18 + 37, 1),
    "eval128": (128, "dense", "eval_matrix", 128, 1),
    "eval-vector128": (128, "dense", "eval", 128, 1),
    "eval-small": (128, "dense", "eval", 4, 1),
    "eval-repeated": (128, "dense", "eval", 128, 5),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def worker(case, variant):
    if case in OPERATIONS:
        operation_worker(case, variant)
        return
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


def binary_apply(matrix, vector, exponent, mod, summation=False):
    result = [0] * len(vector) if summation else vector[:]
    block = vector[:]
    while exponent:
        if exponent & 1:
            result = matrix_vector_multiply(matrix, result, mod)
            if summation:
                result = [(x + y) % mod for x, y in zip(result, block)]
        exponent >>= 1
        if exponent:
            if summation:
                advanced = matrix_vector_multiply(matrix, block, mod)
                block = [(x + y) % mod for x, y in zip(block, advanced)]
            matrix = matrix_multiply(matrix, matrix, mod)
    return result


def binary_sum(matrix, count, mod):
    n = len(matrix)
    power = [[int(i == j) for j in range(n)] for i in range(n)]
    total = [[0] * n for _ in range(n)]
    for bit in bin(count)[2:]:
        advanced = matrix_multiply(power, total, mod)
        total = [[(x + y) % mod for x, y in zip(row, other)] for row, other in zip(total, advanced)]
        power = matrix_multiply(power, power, mod)
        if bit == "1":
            total = [[(x + y) % mod for x, y in zip(row, other)] for row, other in zip(total, power)]
            power = matrix_multiply(power, matrix, mod)
    return total


def horner(matrix, coefficients, vector, mod):
    n = len(matrix)
    if vector is not None:
        result = [0] * n
        for value in reversed(coefficients):
            result = matrix_vector_multiply(matrix, result, mod)
            result = [(x + value * y) % mod for x, y in zip(result, vector)]
        return result
    result = [[0] * n for _ in range(n)]
    for value in reversed(coefficients):
        result = matrix_multiply(matrix, result, mod)
        for i in range(n):
            result[i][i] = (result[i][i] + value) % mod
    return result


def operation_worker(case, variant):
    n, shape, operation, argument, queries = OPERATIONS[case]
    mod, rng = 998244353, random.Random(721)
    if shape == "dense":
        matrix = [[rng.randrange(mod) for _ in range(n)] for _ in range(n)]
    elif shape == "permutation":
        permutation = list(range(n))
        rng.shuffle(permutation)
        matrix = [[int(j == permutation[i]) for j in range(n)] for i in range(n)]
    else:
        matrix = [[int(i == j) for j in range(n)] for i in range(n)]
    vectors = [[rng.randrange(mod) for _ in range(n)] for _ in range(queries)]
    coefficients = [[rng.randrange(mod) for _ in range(argument)] for _ in range(queries)] if operation.startswith("eval") else None
    started = perf_counter()
    form = Frobenius(matrix, mod, seed=11) if variant != "binary" else None
    built = perf_counter()
    results = []
    for index, vector in enumerate(vectors):
        value = coefficients[index] if coefficients is not None else argument + index
        entire = operation.endswith("_matrix")
        if form is not None:
            method = getattr(form, operation.removesuffix("_matrix"))
            result = method(value, None if entire or variant == "materialized" else vector)
            if not entire and variant == "materialized":
                result = matrix_vector_multiply(result, vector, mod)
        elif operation == "pow":
            result = binary_apply(matrix, vector, value, mod)
        elif operation == "sum":
            result = binary_apply(matrix, vector, value, mod, True)
        elif operation == "sum_matrix":
            result = binary_sum(matrix, value, mod)
        else:
            result = horner(matrix, value, None if entire else vector, mod)
        results.append(result)
    finished = perf_counter()
    print(json.dumps(dict(seconds=finished-started, buildSeconds=built-started, querySeconds=finished-built,
                         inputSha256=digest([matrix, vectors, coefficients, argument, operation, mod]), resultSha256=digest(results),
                         blocks=[len(block) for block in form._blocks] if form is not None else None)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--suite", choices=("power", "operations"), default="power")
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
        for case in args.cases or (OPERATIONS if args.suite == "operations" else CASES):
            variants = ["binary", "frobenius"]
            if case in OPERATIONS and not OPERATIONS[case][2].endswith("_matrix"):
                variants.append("materialized")
            samples, expected = {variant: [] for variant in variants}, None
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
            rows.append(dict(case=case, parameters=(OPERATIONS if case in OPERATIONS else CASES)[case], samples=samples,
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
