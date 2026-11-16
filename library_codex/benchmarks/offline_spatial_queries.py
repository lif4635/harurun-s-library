import argparse
from bisect import bisect_left
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


class MinSegTree:
    def __init__(self, xs, ys):
        n = len(xs)
        order = sorted(range(n), key=xs.__getitem__)
        self.xs = [xs[i] for i in order]
        self.order = order
        self.rank = [0] * n
        self.base = base = 1 << max(0, n - 1).bit_length()
        self.data = data = [float("inf")] * (base * 2)
        for i, index in enumerate(order):
            self.rank[index] = i
            data[base + i] = ys[index]
        for v in range(base - 1, 0, -1):
            data[v] = min(data[v * 2], data[v * 2 + 1])

    def set(self, index, y):
        v = self.base + self.rank[index]
        data = self.data
        data[v] = y
        v >>= 1
        while v:
            data[v] = min(data[v * 2], data[v * 2 + 1])
            v >>= 1

    def report(self, left, right, upper):
        lo, hi = bisect_left(self.xs, left), bisect_left(self.xs, right)
        data, base, order = self.data, self.base, self.order
        result, stack = [], [(1, 0, base)]
        while stack:
            v, l, r = stack.pop()
            if hi <= l or r <= lo or data[v] >= upper:
                continue
            if v >= base:
                result.append(order[l])
                continue
            middle = (l + r) >> 1
            stack.append((v * 2, l, middle))
            stack.append((v * 2 + 1, middle, r))
        return result


def worker(case, variant):
    from library_codex.range_query.OfflineRangeKth import offline_range_kth
    from library_codex.range_query.WaveletMatrix import WaveletMatrix
    from library_codex.spatial_structure.PrioritySearchTree import PrioritySearchTree
    from library_codex.benchmarks.baselines.priority_search_tree import PrioritySearchTree as Original
    rng = random.Random(883712)
    build_seconds = None
    if case.startswith("kth"):
        n, q = (64, 64) if case == "kth-small" else (50000, 32 if case == "kth-few" else 50000)
        values = [rng.randrange(16 if case == "kth-duplicates" else n * 4) for _ in range(n)]
        if case == "kth-sorted":
            values.sort()
        queries = []
        for _ in range(q):
            left = rng.randrange(n)
            right = rng.randrange(left + 1, n + 1)
            queries.append((left, right, rng.randrange(right - left)))
        inputs = values, queries
        started = perf_counter()
        if variant == "offline":
            result = offline_range_kth(values, queries)
        else:
            alphabet = sorted(set(values))
            codes = {value: i for i, value in enumerate(alphabet)}
            tree = WaveletMatrix([codes[v] for v in values])
            result = [alphabet[tree.kth_smallest(*query)] for query in queries]
        elapsed = perf_counter() - started
    else:
        n, q = (8192, 128) if case == "points-dense" else (65536, 4096) if case == "points-full" else (32768, 4096)
        xs, ys = list(range(n)), [rng.randrange(n) for _ in range(n)]
        rng.shuffle(xs)
        operations = []
        for i in range(q):
            if case == "points-full":
                operations.append((1, 0, n, 64))
            elif i % 3 == 0:
                operations.append((0, rng.randrange(n), rng.randrange(n)))
            else:
                left = rng.randrange(n)
                width = 8 if case == "points-narrow" else n // 2
                upper = 32 if case == "points-sparse" else n
                operations.append((1, left, min(n, left + width), upper))
        inputs = xs, ys, operations
        started = perf_counter()
        cls = PrioritySearchTree if variant == "priority" else Original if variant == "initial" else MinSegTree
        tree = cls(xs, ys)
        build_seconds = perf_counter() - started
        result = []
        for op in operations:
            if op[0]:
                result.append(tree.report(*op[1:]))
            else:
                tree.set(*op[1:])
        elapsed = perf_counter() - started
        result = [sorted(row) for row in result]
    print(json.dumps(dict(seconds=elapsed, buildSeconds=build_seconds, operationSeconds=None if build_seconds is None else elapsed - build_seconds, inputSha256=hashlib.sha256(json.dumps(inputs).encode()).hexdigest(), resultSha256=hashlib.sha256(json.dumps(result).encode()).hexdigest())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/offline-spatial-queries.json")
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        return
    version = subprocess.check_output([args.python, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("PyPy required")
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    cases = {name: ["wavelet", "offline"] for name in ("kth-small", "kth-random", "kth-few", "kth-duplicates", "kth-sorted")}
    cases.update({name: ["segment", "initial", "priority"] for name in ("points-sparse", "points-dense", "points-narrow", "points-full")})
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        rss = Path(directory) / "rss"
        for case, variants in cases.items():
            samples, expected = {key: [] for key in variants}, None
            for iteration in range(args.repeat):
                order = variants.copy()
                random.Random(iteration + 77).shuffle(order)
                for variant in order:
                    start = perf_counter()
                    run = subprocess.run(["/usr/bin/time", "-f", "%M", "-o", str(rss), args.python, str(Path(__file__).resolve()), "--worker", case, variant], capture_output=True, text=True, check=True, timeout=120)
                    sample = json.loads(run.stdout)
                    sample.update(wallSeconds=perf_counter() - start, peakRssKiB=int(rss.read_text().strip()))
                    current = sample["inputSha256"], sample["resultSha256"]
                    if expected is None:
                        expected = current
                    assert current == expected, case
                    samples[variant].append(sample)
                    print(case, variant, iteration + 1, round(sample["seconds"], 6), flush=True)
            rows.append(dict(case=case, samples=samples, summary={key: dict(medianSeconds=statistics.median(s["seconds"] for s in values), peakRssKiB=max(s["peakRssKiB"] for s in values)) for key, values in samples.items()}))
    paths = ["range_query/OfflineRangeKth.py", "range_query/WaveletMatrix.py", "spatial_structure/PrioritySearchTree.py", "benchmarks/offline_spatial_queries.py", "benchmarks/baselines/priority_search_tree.py"]
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), environment=dict(runtime=version, platform=platform.platform(), cpuInfo=Path("/proc/cpuinfo").read_text().split("model name", 1)[1].splitlines()[0].lstrip("\t: "), affinity=sorted(os.sched_getaffinity(0))), repeat=args.repeat, protocol="fresh sequential PyPy processes; CPU affinity; shuffled order; equal input/output hashes; core and wall time; GNU time peak RSS; not C++ timings; CPU not isolated", sourceSha256={p: hashlib.sha256((ROOT / "library_codex" / p).read_bytes()).hexdigest() for p in paths}, results=rows)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    json.loads(temporary.read_text())
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
