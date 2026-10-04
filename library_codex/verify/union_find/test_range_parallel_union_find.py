import random

import pytest

from library_codex.union_find.RangeParallelUnionFind import RangeParallelUnionFind
from library_codex.union_find.UnionFind import UnionFind


def test_random_ranges_and_component_sums():
    rng = random.Random(815024)
    for n in (1, 2, 3, 7, 8, 9, 31, 32, 33, 200):
        solver = RangeParallelUnionFind(n)
        naive = UnionFind(n)
        values = [rng.randrange(1000) for _ in range(n)]
        sums = values[:]
        calls = []

        def merged(root, old):
            assert solver.find(old) == root
            assert solver.find(root) == root
            sums[root] += sums[old]
            calls.append((root, old))

        for _ in range(3000):
            length = rng.randrange(n + 1)
            first = rng.randrange(n - length + 1)
            second = rng.randrange(n - length + 1)
            solver.merge(first, second, length, merged)
            for offset in range(length):
                naive.merge(first + offset, second + offset)
            for _ in range(10):
                left = rng.randrange(n)
                right = rng.randrange(n)
                assert solver.same(left, right) == naive.same(left, right)
                assert solver.size(left) == naive.size(left)
        for group in naive.groups():
            assert sums[solver.find(group[0])] == sum(values[v] for v in group)
        assert len(calls) == n - naive.component_count


def test_empty_power_of_two_overlap_and_invalid_ranges():
    RangeParallelUnionFind(0).merge(0, 0, 0)
    solver = RangeParallelUnionFind(65)
    solver.merge(0, 1, 32)
    assert solver.size(0) == 33
    solver.merge(32, 33, 32)
    assert solver.size(0) == 65
    for first, second, length in ((-1, 0, 1), (0, -1, 1), (64, 0, 2), (0, 64, 2)):
        with pytest.raises(IndexError):
            solver.merge(first, second, length)
