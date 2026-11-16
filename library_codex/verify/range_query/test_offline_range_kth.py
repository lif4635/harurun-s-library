import random

import pytest

from library_codex.range_query.OfflineRangeKth import offline_range_kth
from library_codex.range_query.WaveletMatrix import WaveletMatrix


def test_random_queries_against_sorting():
    rng = random.Random(7123)
    for n in range(1, 101):
        values = [rng.randrange(-30, 31) for _ in range(n)]
        queries = []
        for _ in range(150):
            left = rng.randrange(n)
            right = rng.randrange(left + 1, n + 1)
            queries.append((left, right, rng.randrange(right - left)))
        original = values.copy(), queries.copy()
        expected = [sorted(values[l:r])[k] for l, r, k in queries]
        assert offline_range_kth(values, queries) == expected
        assert (values, queries) == original


def test_monotone_duplicates_strings_and_empty():
    for values in ([1] * 20, list(range(20)), list(range(19, -1, -1)), ["z", "a", "z", "b"]):
        queries = [(l, r, k) for l in range(len(values)) for r in range(l + 1, len(values) + 1) for k in (0, r - l - 1)]
        assert offline_range_kth(values, iter(queries)) == [sorted(values[l:r])[k] for l, r, k in queries]
    assert offline_range_kth([], []) == []
    assert offline_range_kth([5, 2, 1], []) == []
    for values, queries in (([], [(0, 0, 0)]), ([1], [(0, 1, -1)]), ([1], [(0, 1, 1)]), ([1], [(-1, 1, 0)]), ([1], [(0, 2, 0)])):
        with pytest.raises(ValueError):
            offline_range_kth(values, queries)


def test_large_queries_against_wavelet_matrix():
    rng = random.Random(37133)
    n = 12000
    values = [rng.randrange(1 << 20) for _ in range(n)]
    queries = []
    for _ in range(10000):
        left = rng.randrange(n)
        right = rng.randrange(left + 1, n + 1)
        queries.append((left, right, rng.randrange(right - left)))
    tree = WaveletMatrix(values)
    assert offline_range_kth(values, queries) == [tree.kth_smallest(*query) for query in queries]
