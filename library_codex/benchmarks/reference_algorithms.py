import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
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


def maxmin_ntt(a, b):
    from library_codex.convolution.NTT998 import multiply
    n, m = len(a), len(b)
    if not n or not m:
        return []
    order = sorted([(x, i, 0) for i, x in enumerate(a)] + [(x, i, 1) for i, x in enumerate(b)], reverse=True)
    block = max(1, int(math.sqrt((n + m) * math.log2(n + m))))
    active_a, active_b = [0] * n, [0] * m
    result = [None] * (n + m - 1)
    remaining = len(result)
    for first in range(0, len(order), block):
        current = order[first:first + block]
        x, y = active_a.copy(), active_b.copy()
        for value, i, side in current:
            (y if side else x)[i] = 1
        counts = multiply(x, y)
        pending = [i for i, value in enumerate(counts) if value and result[i] is None]
        for value, i, side in current:
            other = active_a if side else active_b
            length = len(other)
            for pos in pending:
                if result[pos] is None and 0 <= pos - i < length and other[pos - i]:
                    result[pos] = value
                    remaining -= 1
            (active_b if side else active_a)[i] = 1
        if not remaining:
            break
    return result


def ordered_naive(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, value in enumerate(a):
        for j in range(i + 1, len(b)):
            result[i + j] = (result[i + j] + value * b[j]) % 998244353
    return result


def subset_sets(values, k):
    dp = [{0}] + [set() for _ in range(k)]
    for index, value in enumerate(sorted(set(values))):
        for count in range(min(index + 1, k), 0, -1):
            dp[count].update(s + value for s in dp[count - 1])
    return sorted(dp[k])


def interval_list(operations):
    result = []
    for left, right, value in operations:
        current = []
        for lo, hi, old in result:
            if hi <= left or right <= lo:
                current.append((lo, hi, old))
            else:
                if lo < left:
                    current.append((lo, left, old))
                if right < hi:
                    current.append((right, hi, old))
        current.append((left, right, value))
        current.sort()
        result = []
        for lo, hi, old in current:
            if result and result[-1][1] == lo and result[-1][2] == old:
                result[-1] = result[-1][0], hi, old
            else:
                result.append((lo, hi, old))
    return result


def worker(case, variant):
    rng = random.Random(921777)
    if case.startswith("maxmin"):
        from library_codex.convolution.MaxMinConvolution import max_min_conv
        size = 32768 if case.endswith("large") else 4096
        a, b = [rng.randrange(10**9) for _ in range(size)], [rng.randrange(10**9) for _ in range(size)]
        if "monotone" in case:
            a, b = list(range(size)), list(range(size))
        data = a, b
        started = perf_counter()
        value = max_min_conv(a, b) if variant == "bitset" else maxmin_ntt(a, b)
    elif case.startswith("ordered"):
        from library_codex.convolution.OrderedConvolution import ordered_conv
        from library_codex.benchmarks.baselines.ordered_convolution import ordered_conv as original
        size = 32768 if case.endswith("large") else 4096
        a, b = [rng.randrange(998244353) for _ in range(size)], [rng.randrange(998244353) for _ in range(size)]
        data = a, b
        started = perf_counter()
        value = ordered_conv(a, b) if variant == "ntt" else original(a, b) if variant == "initial" else ordered_naive(a, b)
    elif case == "subset":
        from library_codex.optimization.FixedSizeSubsetSum import fixed_size_subset_sums
        values = rng.sample(range(-500, 1000), 50)
        data = values, 12
        started = perf_counter()
        value = fixed_size_subset_sums(values, 12) if variant == "bitset" else subset_sets(values, 12)
    elif case.startswith("interval"):
        from library_codex.ordered_set.IntervalMap import IntervalMap
        size = 40 if case == "interval-small" else 4000
        operations = [(2 * i, 2 * i + 1, i % 3) for i in range(size)]
        for _ in range(size):
            i = rng.randrange(size)
            operations.append((2 * i, 2 * i + rng.randrange(1, 5), rng.randrange(3)))
        data = operations
        started = perf_counter()
        if variant == "treap":
            tree = IntervalMap()
            for left, right, color in operations:
                tree.assign(left, right, color)
            value = tree.items()
        else:
            value = interval_list(operations)
    else:
        from library_codex.shortest_path.ImplicitDijkstra import implicit_dijkstra
        from library_codex.shortest_path.Dijkstra import dijkstra
        width = 180
        data = width

        def adjacent(v):
            if v % width:
                yield v - 1, 1
            if v % width < width - 1:
                yield v + 1, 1
            if v >= width:
                yield v - width, 1
            if v + width < width * width:
                yield v + width, 1

        started = perf_counter()
        if variant == "implicit":
            distance, _ = implicit_dijkstra([0], adjacent)
            value = [distance[v] for v in range(width * width)]
        else:
            graph = [list(adjacent(v)) for v in range(width * width)]
            value = dijkstra(graph)[0]
    elapsed = perf_counter() - started
    print(json.dumps(dict(seconds=elapsed, inputSha256=hashlib.sha256(json.dumps(data).encode()).hexdigest(), resultSha256=hashlib.sha256(json.dumps(value).encode()).hexdigest())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/reference-algorithms.json")
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        return
    version = subprocess.check_output([args.python, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("PyPy required")
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    cases = {"maxmin-random": ["ntt", "bitset"], "maxmin-monotone": ["ntt", "bitset"], "maxmin-large": ["ntt", "bitset"], "ordered": ["naive", "initial", "ntt"], "ordered-large": ["naive", "initial", "ntt"], "subset": ["sets", "bitset"], "interval-small": ["list", "treap"], "interval-large": ["list", "treap"], "implicit": ["explicit", "implicit"]}
    if args.cases:
        cases = {key: cases[key] for key in args.cases}
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        rss = Path(directory) / "rss"
        for case, variants in cases.items():
            samples = {key: [] for key in variants}
            expected = None
            for iteration in range(args.repeat):
                order = variants.copy()
                random.Random(91 + iteration).shuffle(order)
                for variant in order:
                    start = perf_counter()
                    run = subprocess.run(["/usr/bin/time", "-f", "%M", "-o", str(rss), args.python, str(Path(__file__).resolve()), "--worker", case, variant], capture_output=True, text=True, check=True, timeout=240)
                    sample = json.loads(run.stdout)
                    sample.update(wallSeconds=perf_counter() - start, peakRssKiB=int(rss.read_text().strip()))
                    current = sample["inputSha256"], sample["resultSha256"]
                    if expected is None:
                        expected = current
                    assert current == expected, case
                    samples[variant].append(sample)
                    print(case, variant, iteration + 1, round(sample["seconds"], 6), flush=True)
            rows.append(dict(case=case, samples=samples, summary={key: dict(medianSeconds=statistics.median(s["seconds"] for s in values), peakRssKiB=max(s["peakRssKiB"] for s in values)) for key, values in samples.items()}))
    paths = ["shortest_path/ImplicitDijkstra.py", "shortest_path/Dijkstra.py", "ordered_set/IntervalMap.py", "ordered_set/TreapSet.py", "convolution/NTT998.py", "convolution/OrderedConvolution.py", "convolution/MaxMinConvolution.py", "optimization/FixedSizeSubsetSum.py", "benchmarks/reference_algorithms.py", "benchmarks/baselines/ordered_convolution.py"]
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), environment=dict(runtime=version, platform=platform.platform(), cpuInfo=Path("/proc/cpuinfo").read_text().split("model name", 1)[1].splitlines()[0].lstrip("\t: "), affinity=sorted(os.sched_getaffinity(0))), repeat=args.repeat, protocol="fresh sequential PyPy processes; CPU affinity; shuffled order; equal input/output hashes; core and wall time; GNU time peak RSS; not C++ timings; CPU not isolated", reference="qandori/cp-library ceec97a52d734d23f762b9c5e322b2b53df0cf9e convolution/max_min_convolution.hpp; Python port using local NTT998", sourceSha256={p: hashlib.sha256((ROOT / "library_codex" / p).read_bytes()).hexdigest() for p in paths}, results=rows)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    json.loads(temporary.read_text())
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
