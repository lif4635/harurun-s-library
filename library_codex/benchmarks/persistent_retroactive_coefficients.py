import argparse
import copy
from datetime import datetime, timezone
import hashlib
import heapq
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


def digest(value):
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def worker(case, variant):
    rng = random.Random(523744)
    from library_codex.sequence_structure.PersistentDeque import PersistentDeque
    from library_codex.string.PersistentString import PersistentString
    from library_codex.tree.PersistentLinkCutTree import PersistentLinkCutTree
    from library_codex.tree.LinkCutTree import LinkCutTree
    from library_codex.ordered_set.RetroactivePriorityQueue import RetroactivePriorityQueue
    from library_codex.fps.SparseCoefficient import inv_coeff, exp_coeff, pow_coeff
    if variant == "initial":
        from library_codex.benchmarks.baselines.sparse_coefficient import inv_coeff, exp_coeff, pow_coeff
    from library_codex.fps.SparseFormalPowerSeries import sparse_inverse, sparse_exponential, sparse_power
    storage = None
    if case == "deque-ends":
        n, q = 20000, 4000
        values = list(range(n))
        inputs = values, q
        started = perf_counter()
        result = []
        if variant == "adopted":
            tree = PersistentDeque(values)
            version = 0
            for i in range(q):
                version = tree.push_back(i, tree.pop_front(version))
                result.append(tree.get(0, version))
            storage = tree.node_count()
        else:
            versions = [PersistentString(values)]
            for i in range(q):
                tree = versions[-1].deleted(0, 1).inserted([i], n - 1)
                versions.append(tree)
                result.append(tree[0])
        seconds = perf_counter() - started
    elif case.startswith("deque"):
        n, q = (64, 512) if case == "deque-small" else (20000, 4000)
        values = list(range(n))
        operations = [(rng.randrange(i + 1) if case == "deque-branch" else i, rng.randrange(n), rng.randrange(1 << 20)) for i in range(q)]
        inputs = values, operations
        started = perf_counter()
        result = []
        if variant == "adopted":
            tree = PersistentDeque(values)
            for base, index, value in operations:
                version = tree.set(index, value, base)
                result.append(tree.get(index, version))
                result.append(tree.get(index, base))
            storage = tree.node_count()
        else:
            versions = [PersistentString(values)]
            for base, index, value in operations:
                version = versions[base].replaced(index, index + 1, [value])
                versions.append(version)
                result.extend((version[index], versions[base][index]))
        seconds = perf_counter() - started
    elif case.startswith("tree"):
        n, q = (512, 128) if case == "tree-branch" else (2048, 256)
        values = list(range(n))
        operations = [(0 if case == "tree-branch" else i, 0, n - 1) for i in range(q)]
        inputs = values, operations
        started = perf_counter()
        result = []
        if variant == "adopted":
            tree = PersistentLinkCutTree(values, edges=((i - 1, i) for i in range(1, n)))
            for base, u, v in operations:
                version, answer = tree.prod(u, v, base)
                result.append(answer)
            storage = tree.node_count()
        else:
            tree = LinkCutTree(values)
            for i in range(1, n):
                tree.link(i - 1, i)
            versions = [tree]
            for base, u, v in operations:
                tree = copy.copy(versions[base])
                for field in tree.__slots__:
                    value = getattr(tree, field)
                    if isinstance(value, (list, bytearray)):
                        setattr(tree, field, value.copy() if isinstance(value, list) else bytearray(value))
                result.append(tree.path_fold(u, v))
                versions.append(tree)
        seconds = perf_counter() - started
    elif case.startswith("retro"):
        n, q = (32, 1000) if case == "retro-small" else (8192, 4096)
        operations = [(rng.randrange(n), rng.randrange(3), rng.randrange(-100, 101)) for _ in range(q)]
        inputs = n, operations
        started = perf_counter()
        result = []
        if variant == "adopted":
            tree = RetroactivePriorityQueue(n)
            for t, kind, value in operations:
                if kind == 1:
                    tree.set_push(t, value)
                elif kind == 2:
                    tree.set_pop(t)
                else:
                    tree.erase(t)
                result.append((tree.peek(), tree.sum(), tree.popped_sum(), len(tree)))
        else:
            slots = [(0, 0)] * n
            for t, kind, value in operations:
                slots[t] = kind, value
                heap, popped, total = [], 0, 0
                for k, v in slots:
                    if k == 1:
                        heapq.heappush(heap, v)
                        total += v
                    elif k == 2 and heap:
                        x = heapq.heappop(heap)
                        popped += x
                        total -= x
                result.append((heap[0] if heap else None, total, popped, len(heap)))
        seconds = perf_counter() - started
    else:
        if case == "coeff-inverse":
            series, index, exponent = [1, 3] + [0] * 29 + [7], 1000000, 0
        elif case == "coeff-exp-small":
            series, index, exponent = [0, 3, 5, 7], 1000, 0
        elif case in ("coeff-exp", "coeff-exp-far"):
            series, index, exponent = [0, 3, 5], 10000000 if case.endswith("far") else 1000000, 0
        else:
            series, index, exponent = [1, 3, 5], 10000000 if case.endswith("far") else 1000000, 10**9
        inputs = series, index, exponent
        started = perf_counter()
        if case == "coeff-inverse":
            result = inv_coeff(series, index) if variant != "baseline" else sparse_inverse(series, index + 1)[index]
        elif case.startswith("coeff-exp"):
            result = exp_coeff(series, index) if variant != "baseline" else sparse_exponential(series, index + 1)[index]
        else:
            result = pow_coeff(series, exponent, index) if variant != "baseline" else sparse_power(series, exponent, index + 1)[index]
        seconds = perf_counter() - started
    print(json.dumps(dict(seconds=seconds, inputSha256=digest(inputs), resultSha256=digest(result), storageNodes=storage)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/persistent-retroactive-coefficients.json")
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        return
    version = subprocess.check_output([args.python, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("PyPy required")
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    cases = args.cases or ["deque-small", "deque-linear", "deque-branch", "deque-ends", "tree-linear", "tree-branch", "retro-small", "retro-edits", "coeff-inverse", "coeff-exp-small", "coeff-exp", "coeff-power", "coeff-exp-far", "coeff-power-far"]
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        rss = Path(directory) / "rss"
        for case in cases:
            samples, expected = {key: [] for key in (("baseline", "initial", "adopted") if case.startswith("coeff") else ("baseline", "adopted"))}, None
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
            rows.append(dict(case=case, samples=samples, summary={key: dict(medianSeconds=statistics.median(s["seconds"] for s in values), peakRssKiB=max(s["peakRssKiB"] for s in values)) for key, values in samples.items()}))
    paths = ["sequence_structure/PersistentDeque.py", "string/PersistentString.py", "tree/PersistentLinkCutTree.py", "tree/LinkCutTree.py", "sequence_structure/PersistentArray.py", "ordered_set/RetroactivePriorityQueue.py", "fps/SparseCoefficient.py", "fps/SparseFormalPowerSeries.py", "polynomial/PolynomialMatrixRecurrence.py", "benchmarks/persistent_retroactive_coefficients.py"]
    paths.append("benchmarks/baselines/sparse_coefficient.py")
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), environment=dict(runtime=version, platform=platform.platform(), cpuInfo=Path("/proc/cpuinfo").read_text().split("model name", 1)[1].splitlines()[0].lstrip("\t: "), affinity=sorted(os.sched_getaffinity(0))), repeat=args.repeat, protocol="fresh sequential PyPy processes; shuffled order; matching input/output hashes; core and wall time; GNU time RSS; CPU not isolated; not C++/Nim timings", sourceSha256={p: hashlib.sha256((ROOT / "library_codex" / p).read_bytes()).hexdigest() for p in paths}, results=rows)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    json.loads(temporary.read_text())
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
