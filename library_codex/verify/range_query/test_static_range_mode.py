import itertools
import random
from collections import Counter

import pytest

from library_codex.range_query.StaticRangeMode import StaticRangeMode


def check_queries(values, width, queries):
    table = StaticRangeMode(values, width)
    for left, right in queries:
        counts = Counter(values[left:right])
        best = max(counts.values(), default=0)
        value = next((value for value in values[left:right] if counts[value] == best), None)
        assert table.mode(left, right) == (value, best)
        assert table.count(value, left, right) == best
    assert table.tolist() == values
    assert str(table) == str(values)
    assert repr(table) == "StaticRangeMode(%r)" % values
    copy = table.tolist()
    copy.append("extra")
    assert table.tolist() == values


def test_exhaustive_ties_and_boundaries():
    for n in range(7):
        for values in itertools.product(range(2), repeat=n):
            values = list(values)
            queries = [(left, right) for left in range(n + 1) for right in range(left, n + 1)]
            for width in (1, 2, 3, n + 1):
                check_queries(values, width, queries)


def test_random_ranges_and_generic_values():
    rng = random.Random(871246)
    for n in (1, 2, 5, 20, 100, 313):
        for distinct in (1, 2, 8, n + 1):
            values = [rng.randrange(distinct) for _ in range(n)]
            queries = []
            for _ in range(400):
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                queries.append((left, right))
            for width in (None, 1, 7, n + 1):
                check_queries(values, width, queries)
    check_queries(["b", None, ("a",), None, "b"], 2, [(0, 5), (1, 4), (2, 5)])


def test_invalid_ranges_and_block_size():
    for width in (0, -1):
        with pytest.raises(ValueError):
            StaticRangeMode([], width)
    table = StaticRangeMode([1, 2])
    for left, right in ((-1, 1), (1, 0), (0, 3)):
        with pytest.raises(IndexError):
            table.mode(left, right)
