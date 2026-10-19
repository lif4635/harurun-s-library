import itertools
import random

import pytest

from library_codex.range_query.OfflineRangeInversions import range_inversions


def naive(values, left, right):
    return sum(values[i] > values[j] for i in range(left, right) for j in range(i + 1, right))


def test_exhaustive_duplicates():
    for n in range(7):
        queries = [(l, r) for l in range(n + 1) for r in range(l, n + 1)]
        for values in itertools.product(range(3), repeat=n):
            assert range_inversions(values, queries) == [naive(values, l, r) for l, r in queries]


def test_random_unsorted_queries_and_input_preservation():
    rng = random.Random(379058)
    for n in (0, 1, 2, 10, 99, 300):
        for q in (0, 1, 2, 10, 100, 1000):
            values = [rng.randrange(-50, 50) for _ in range(n)]
            queries = []
            for _ in range(q):
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                queries.append((left, right))
            original = values[:], queries[:]
            expected = [naive(values, l, r) for l, r in queries]
            assert range_inversions(values, queries) == expected
            assert (values, queries) == original
            assert range_inversions(iter(values), iter(queries)) == expected


def test_large_results_and_single_value():
    n = 100000
    assert range_inversions(range(n, 0, -1), [(0, n), (1, n)]) == [n * (n - 1) // 2, (n - 1) * (n - 2) // 2]
    assert range_inversions([7] * 1000, [(0, 1000), (50, 900)]) == [0, 0]
    assert range_inversions([], [(0, 0)] * 3) == [0, 0, 0]
    assert range_inversions(["c", "a", "b", "a"], [(0, 4), (1, 3)]) == [4, 0]


def test_invalid_ranges():
    for left, right in ((-1, 1), (1, 0), (0, 3)):
        with pytest.raises(IndexError):
            range_inversions([1, 2], [(left, right)])
