import argparse
import gc
import json
import random
import resource
import subprocess
import sys
from operator import add
from pathlib import Path
from statistics import median
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.ordered_set.BinaryTrieMonoid import BinaryTrieMonoid
from library_codex.segment_tree.DynamicSegmentTree import DynamicSegmentTree


def exercise(implementation, keys, queries):
    tree = BinaryTrieMonoid(add, 0, 30) if implementation == "trie" else DynamicSegmentTree(0, 1 << 30, add, 0)
    start = perf_counter()
    for i, key in enumerate(keys):
        tree.set(key, i)
    built = perf_counter()
    checksum = 0
    for left, right in queries:
        checksum += tree.prod(left, right)
    queried = perf_counter()
    for i, key in enumerate(keys):
        tree.set(key, -i)
    updated = perf_counter()
    return tree, checksum, [built - start, queried - built, updated - queried]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation", choices=["trie", "segtree"])
    parser.add_argument("--size", type=int, default=20000)
    parser.add_argument("--repeat", type=int, default=7)
    args = parser.parse_args()
    if args.implementation is None:
        rows = []
        for impl in ("segtree", "trie"):
            row = json.loads(subprocess.check_output(
                [sys.executable, __file__, "--implementation", impl, "--size", str(args.size),
                 "--repeat", str(args.repeat)], text=True))
            rows.append(row)
            print(json.dumps(row), flush=True)
        assert rows[0]["checksum"] == rows[1]["checksum"]
        return
    rng = random.Random(91802)
    keys = rng.sample(range(1 << 30), args.size)
    queries = [sorted([rng.randrange(1 << 30), rng.randrange(1 << 30)]) for _ in keys]
    for _ in range(3):
        exercise(args.implementation, keys[:2000], queries[:2000])
    times = []
    for _ in range(args.repeat):
        gc.collect()
        tree, checksum, timing = exercise(args.implementation, keys, queries)
        times.append(timing)
        nodes = len(tree.data)
        del tree
    print(json.dumps({
        "implementation": args.implementation, "n": args.size, "checksum": checksum,
        "milliseconds": [round(median(row[i] for row in times) * 1000, 3) for i in range(3)],
        "allocatedNodes": nodes,
        "peakRssMiB": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
    }))


if __name__ == "__main__":
    main()
