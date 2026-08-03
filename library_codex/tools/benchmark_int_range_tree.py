"""PyPy benchmark for callback-free integer lazy segment trees."""

import argparse
import random
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.segment_tree.RangeAddAssignRangeStats import RangeAddAssignRangeStats
from library_codex.segment_tree.RangeAffineRangeSum import RangeAffineRangeSum
from library_codex.segment_tree.LazySegmentTree import LazySegmentTree
from library_codex.segment_tree.SegmentTreeBeats import SegmentTreeBeats


INF = float("inf")


def make_operations(n, q, seed):
    rng = random.Random(seed)
    operations = []
    for _ in range(q):
        left = rng.randrange(n)
        right = rng.randrange(left + 1, n + 1)
        command = rng.randrange(5)
        value = rng.randrange(-1000, 1001) if command < 2 else 0
        operations.append((command, left, right, value))
    return operations


def make_affine_operations(n, q, seed):
    rng = random.Random(seed)
    operations = []
    for _ in range(q):
        left = rng.randrange(n)
        right = rng.randrange(left + 1, n + 1)
        if rng.randrange(3):
            operations.append((0, left, right, rng.randrange(1000), rng.randrange(1000)))
        else:
            operations.append((1, left, right, 0, 0))
    return operations


def generic_tree(values):
    def operation(left, right):
        return left[0] + right[0], min(left[1], right[1]), max(left[2], right[2])

    def mapping(action, stats, length):
        assigned, added = action
        if assigned is None:
            return stats[0] + added * length, stats[1] + added, stats[2] + added
        value = assigned + added
        return value * length, value, value

    def composition(new, old):
        new_assign, new_add = new
        old_assign, old_add = old
        if new_assign is not None:
            return new_assign, new_add
        return old_assign, old_add + new_add

    return LazySegmentTree(
        [(value, value, value) for value in values],
        operation,
        (0, INF, -INF),
        mapping,
        composition,
    )


def generic_affine_tree(values, mod):
    def operation(left, right):
        return (left + right) % mod

    def mapping(action, total, length):
        multiplier, addend = action
        return (multiplier * total + addend * length) % mod

    def composition(new, old):
        new_multiplier, new_addend = new
        old_multiplier, old_addend = old
        return (
            new_multiplier * old_multiplier % mod,
            (new_multiplier * old_addend + new_addend) % mod,
        )

    return LazySegmentTree(values, operation, 0, mapping, composition)


def run_generic(tree, operations):
    checksum = 0
    for command, left, right, value in operations:
        if command == 0:
            tree.apply(left, right, (None, value))
        elif command == 1:
            tree.apply(left, right, (value, 0))
        else:
            checksum ^= hash(tree.prod(left, right)[command - 2])
    return checksum


def run_specialized(tree, operations):
    checksum = 0
    for command, left, right, value in operations:
        if command == 0:
            tree.range_add(left, right, value)
        elif command == 1:
            tree.range_assign(left, right, value)
        elif command == 2:
            checksum ^= tree.range_sum(left, right)
        elif command == 3:
            checksum ^= hash(tree.range_min(left, right))
        else:
            checksum ^= hash(tree.range_max(left, right))
    return checksum


def run_beats(tree, operations):
    checksum = 0
    for command, left, right, value in operations:
        if command == 0:
            tree.range_add(left, right, value)
        elif command == 1:
            tree.range_assign(left, right, value)
        elif command == 2:
            checksum ^= tree.range_sum(left, right)
        elif command == 3:
            checksum ^= hash(tree.range_min(left, right))
        else:
            checksum ^= hash(tree.range_max(left, right))
    return checksum


def run_affine(tree, operations, specialized):
    checksum = 0
    for command, left, right, multiplier, addend in operations:
        if command == 0:
            if specialized:
                tree.apply(left, right, multiplier, addend)
            else:
                tree.apply(left, right, (multiplier, addend))
        elif specialized:
            checksum ^= tree.range_sum(left, right)
        else:
            checksum ^= tree.prod(left, right)
    return checksum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", choices=("stats", "affine"), default="stats")
    parser.add_argument("--backend", choices=("generic", "beats", "specialized"), required=True)
    parser.add_argument("--size", type=int, default=200000)
    parser.add_argument("--queries", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=8300)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    values = [rng.randrange(-1000, 1001) for _ in range(args.size)]
    if args.workload == "affine":
        if args.backend == "beats":
            parser.error("the beats backend does not support affine updates")
        mod = 998244353
        values = [value % mod for value in values]
        operations = make_affine_operations(args.size, args.queries, args.seed + 1)
        started = perf_counter()
        if args.backend == "generic":
            tree = generic_affine_tree(values, mod)
            specialized = False
        else:
            tree = RangeAffineRangeSum(values, mod)
            specialized = True
        build_time = perf_counter() - started
        started = perf_counter()
        checksum = run_affine(tree, operations, specialized)
        solve_time = perf_counter() - started
        print(
            f"workload=affine backend={args.backend} "
            f"size={args.size} queries={args.queries}"
        )
        print(f"build={build_time:.6f}s solve={solve_time:.6f}s total={build_time + solve_time:.6f}s")
        print(f"checksum={checksum}")
        return

    operations = make_operations(args.size, args.queries, args.seed + 1)
    started = perf_counter()
    if args.backend == "generic":
        tree = generic_tree(values)
        build_time = perf_counter() - started
        started = perf_counter()
        checksum = run_generic(tree, operations)
    elif args.backend == "beats":
        tree = SegmentTreeBeats(values)
        build_time = perf_counter() - started
        started = perf_counter()
        checksum = run_beats(tree, operations)
    else:
        tree = RangeAddAssignRangeStats(values)
        build_time = perf_counter() - started
        started = perf_counter()
        checksum = run_specialized(tree, operations)
    solve_time = perf_counter() - started
    print(f"workload=stats backend={args.backend} size={args.size} queries={args.queries}")
    print(f"build={build_time:.6f}s solve={solve_time:.6f}s total={build_time + solve_time:.6f}s")
    print(f"checksum={checksum}")


if __name__ == "__main__":
    main()
