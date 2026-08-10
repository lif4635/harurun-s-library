"""Compare segment-tree and square-decomposition query/update workloads."""

import argparse
import random
import sys
import time
from math import isqrt
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[2]))

from library_codex.segment_tree.SortableSegmentTree import SortableSegmentTree


class SquareDecomposition:
    def __init__(self, values):
        self.values = list(values)
        self.size = len(values)
        self.block = max(32, isqrt(max(1, self.size)) + 1)
        count = (self.size + self.block - 1) // self.block
        self.sums = [0] * count
        for index, value in enumerate(values):
            self.sums[index // self.block] += value

    def update(self, index, value):
        block = index // self.block
        self.sums[block] += value - self.values[index]
        self.values[index] = value

    def query(self, left, right):
        result = 0
        while left < right and left % self.block:
            result += self.values[left]
            left += 1
        while left + self.block <= right:
            result += self.sums[left // self.block]
            left += self.block
        while left < right:
            result += self.values[left]
            left += 1
        return result


def run(structure, operations):
    checksum = 0
    started = time.perf_counter()
    for kind, first, second in operations:
        if kind:
            structure.update(first, first, second)
        else:
            checksum = (checksum + structure.query(first, second)) & ((1 << 64) - 1)
    return time.perf_counter() - started, checksum


def run_square(structure, operations):
    checksum = 0
    started = time.perf_counter()
    for kind, first, second in operations:
        if kind:
            structure.update(first, second)
        else:
            checksum = (checksum + structure.query(first, second)) & ((1 << 64) - 1)
    return time.perf_counter() - started, checksum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=100000)
    parser.add_argument("--queries", type=int, default=100000)
    args = parser.parse_args()
    rng = random.Random(821704)
    values = [rng.randrange(10 ** 6) for _ in range(args.size)]
    operations = []
    for _ in range(args.queries):
        if rng.randrange(5) == 0:
            operations.append((1, rng.randrange(args.size), rng.randrange(10 ** 6)))
        else:
            left = rng.randrange(args.size)
            right = rng.randrange(left + 1, args.size + 1)
            operations.append((0, left, right))

    square_time, square_checksum = run_square(
        SquareDecomposition(values), operations
    )
    tree_time, tree_checksum = run(
        SortableSegmentTree(range(args.size), values), operations
    )
    if square_checksum != tree_checksum:
        raise AssertionError("sortable segment tree checksum mismatch")
    print(f"size={args.size} queries={args.queries}")
    print(f"square={square_time:.6f}s")
    print(f"segment_tree={tree_time:.6f}s")
    print(f"ratio={square_time / tree_time:.3f}x")
    print(f"total={tree_time:.6f}s")
    print(f"checksum={tree_checksum}")


if __name__ == "__main__":
    main()
