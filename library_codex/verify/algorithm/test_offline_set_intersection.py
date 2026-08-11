import random

import pytest

from library_codex.algorithm.OfflineSetIntersection import intersection_sizes


def test_random_against_sets():
    random.seed(20260811)
    for n in range(1, 15):
        for _ in range(80):
            rows = [
                [random.randrange(-8, 9) for _ in range(random.randrange(12))]
                for _ in range(n)
            ]
            queries = [
                (random.randrange(n), random.randrange(n))
                for _ in range(random.randrange(30))
            ]
            expected = [len(set(rows[i]) & set(rows[j])) for i, j in queries]
            assert intersection_sizes(rows, queries) == expected


def test_empty_and_invalid_index():
    assert intersection_sizes([], []) == []
    assert intersection_sizes([[1, 1, 2]], [(0, 0)]) == [2]
    with pytest.raises(IndexError):
        intersection_sizes([[1]], [(0, 1)])
