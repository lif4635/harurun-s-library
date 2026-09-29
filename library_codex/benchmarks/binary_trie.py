import argparse
import gc
import json
import platform
import random
import resource
import subprocess
import sys
from pathlib import Path
from statistics import median
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.benchmarks._binary_trie_baseline import BinaryTrie as Baseline
from library_codex.ordered_set.BinaryTrie import BinaryTrie


def inputs(case, n):
    rng = random.Random(92471)
    bits = 60 if case == "wide" else 30
    if case == "dense":
        values = list(range(n))
        rng.shuffle(values)
    elif case == "duplicates":
        values = [rng.randrange(128) for _ in range(n)]
    elif case == "prefix":
        values = [(1 << 29) + rng.randrange(1 << 16) for _ in range(n)]
    else:
        values = [rng.randrange(1 << bits) for _ in range(n)]
    queries = [rng.randrange(1 << bits) for _ in range(n)]
    return bits, values, queries


def exercise(cls, case, bits, values, queries):
    tree = cls(bits)
    start = perf_counter()
    for x in values:
        tree.add(x)
    built = perf_counter()
    build_nodes = len(tree.count)
    build_cells = sum(len(getattr(tree, name)) for name in cls.__slots__ if isinstance(getattr(tree, name), list))
    answer = 0
    for i, x in enumerate(queries):
        answer += tree.xor_min(x)
        answer += tree.kth(i % len(values))
        answer += tree.bisect_left(x)
    queried = perf_counter()
    for i, x in enumerate(values):
        tree.discard(x)
        tree.add(queries[i])
    mixed = perf_counter()
    tree.xor_all(17)
    answer += tree.min() + tree.max()
    return tree, answer, [built - start, queried - built, mixed - queried], build_nodes, build_cells


def worker(args):
    cls = Baseline if args.implementation == "baseline" else BinaryTrie
    bits, values, queries = inputs(args.case, args.size)
    if not args.memory:
        for _ in range(3):
            exercise(cls, args.case, bits, values[:2000], queries[:2000])
    times = []
    answer = None
    for _ in range(1 if args.memory else args.repeat):
        gc.collect()
        tree, checksum, timing, build_nodes, build_cells = exercise(cls, args.case, bits, values, queries)
        assert answer is None or answer == checksum
        answer = checksum
        times.append(timing)
        nodes = len(tree.count)
        cells = sum(len(getattr(tree, name)) for name in cls.__slots__ if isinstance(getattr(tree, name), list))
        del tree
    print(json.dumps({
        "case": args.case, "implementation": args.implementation, "checksum": answer,
        "milliseconds": [round(median(row[i] for row in times) * 1000, 3) for i in range(3)],
        "allocatedNodes": nodes, "listCells": cells,
        "buildNodes": build_nodes, "buildListCells": build_cells,
        "peakRssMiB": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
    }), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=20000)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--case", choices=["random", "dense", "duplicates", "prefix", "wide"])
    parser.add_argument("--implementation", choices=["baseline", "compressed"])
    parser.add_argument("--memory", action="store_true")
    args = parser.parse_args()
    if args.implementation:
        worker(args)
        return
    print(json.dumps({"runtime": platform.python_implementation(), "version": platform.python_version(),
                      "n": args.size, "columns": ["build", "query", "mixed"]}), flush=True)
    for case in [args.case] if args.case else ["random", "dense", "duplicates", "prefix", "wide"]:
        rows = []
        for implementation in ["baseline", "compressed"]:
            command = [sys.executable, __file__, "--size", str(args.size), "--repeat", str(args.repeat),
                       "--case", case, "--implementation", implementation]
            row = json.loads(subprocess.check_output(command, text=True))
            memory = json.loads(subprocess.check_output(command + ["--memory"], text=True))
            row["peakRssMiB"] = memory["peakRssMiB"]
            rows.append(row)
            print(json.dumps(row), flush=True)
        assert rows[0]["checksum"] == rows[1]["checksum"]


if __name__ == "__main__":
    main()
