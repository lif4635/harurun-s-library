import argparse
import gc
import hashlib
import inspect
import json
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from library_codex.benchmarks._dsu_on_tree_baseline import DSUOnTree as Baseline
from library_codex.tree.DSUOnTree import DSUOnTree


def make_tree(size, family, seed):
    rng = random.Random(seed)
    tree = [[] for _ in range(size)]
    for v in range(1, size):
        p = rng.randrange(v) if family == "random" else v - 1 if family == "chain" else 0 if family == "star" else (v - 1) // 2
        tree[p].append(v)
        tree[v].append(p)
    return tree


def exercise(cls, tree):
    before = perf_counter()
    solver = cls(tree)
    built = perf_counter()
    counts = [0] * 97
    distinct = [0]
    answers = [0] * len(tree)
    calls = [0, 0]

    def add(v):
        color = v % 97
        if not counts[color]:
            distinct[0] += 1
        counts[color] += 1
        calls[0] += 1

    def remove(v):
        color = v % 97
        counts[color] -= 1
        if not counts[color]:
            distinct[0] -= 1
        calls[1] += 1

    def query(v):
        answers[v] = distinct[0]

    started = perf_counter()
    solver.run(add, query, remove)
    ended = perf_counter()
    return built - before, ended - started, answers, calls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=100000)
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--family", choices=["random", "chain", "star", "balanced"])
    parser.add_argument("--implementation", choices=["baseline", "reverse"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reverse-order", action="store_true")
    args = parser.parse_args()
    if not args.implementation:
        result = []
        for family in ["random", "chain", "star", "balanced"]:
            rows = []
            for implementation in (["reverse", "baseline"] if args.reverse_order else ["baseline", "reverse"]):
                command = [sys.executable, __file__, "--size", str(args.size), "--repeat", str(args.repeat), "--family", family, "--implementation", implementation]
                row = json.loads(subprocess.check_output(command))
                rows.append(row)
                result.append(row)
                print(json.dumps(row), flush=True)
            assert rows[0]["outputHash"] == rows[1]["outputHash"]
            assert rows[0]["calls"] == rows[1]["calls"]
        if args.output:
            from library_codex.benchmarks.library_checker import atomic_write, json_bytes
            atomic_write(args.output, json_bytes(result))
        return
    cls = Baseline if args.implementation == "baseline" else DSUOnTree
    for _ in range(3):
        exercise(cls, make_tree(3000, args.family, 92471))
    tree = make_tree(args.size, args.family, 92471)
    samples = []
    for _ in range(args.repeat):
        gc.collect()
        built, ran, answer, calls = exercise(cls, tree)
        samples.append([built, ran])
    print(json.dumps(dict(family=args.family, implementation=args.implementation, size=args.size,
        runtime=sys.version, sourceSha256=hashlib.sha256(inspect.getsource(cls).encode()).hexdigest(),
        buildMs=statistics.median(row[0] for row in samples) * 1000,
        runMs=statistics.median(row[1] for row in samples) * 1000,
        samples=samples, calls=calls, outputHash=hashlib.sha256(bytes(answer)).hexdigest(),
        peakRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)))


if __name__ == "__main__":
    main()
