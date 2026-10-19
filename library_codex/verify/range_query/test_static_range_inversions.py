import itertools
import random

import pytest

from library_codex.range_query.StaticRangeInversions import StaticRangeInversions


def naive(values, left, right):
    return sum(values[i] > values[j] for i in range(left, right) for j in range(i + 1, right))


def test_exhaustive_duplicates_and_block_boundaries():
    for n in range(7):
        for values in itertools.product(range(3), repeat=n):
            for width in (1, 2, 3, n + 1):
                table = StaticRangeInversions(values, width)
                for left in range(n + 1):
                    for right in range(left, n + 1):
                        assert table.query(left, right) == naive(values, left, right)


def test_random_ranges_and_negative_values():
    rng = random.Random(819036)
    for n in (1, 2, 7, 16, 65, 100, 313):
        for distinct in (1, 3, n + 1):
            values = [rng.randrange(-distinct, distinct) for _ in range(n)]
            queries = []
            for _ in range(150):
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                queries.append((left, right))
            expected = [naive(values, l, r) for l, r in queries]
            for width in (None, 1, 7, n + 1):
                table = StaticRangeInversions(values, width)
                assert [table.query(l, r) for l, r in queries] == expected


def test_ordered_inputs_and_large_result():
    n = 100000
    table = StaticRangeInversions(range(n, 0, -1))
    assert table.query(0, n) == n * (n - 1) // 2
    assert table.query(317, 90001) == 89684 * 89683 // 2
    table = StaticRangeInversions(range(1000))
    assert table.query(123, 987) == 0


def test_display_copy_generic_values_and_errors():
    values = ["c", "a", "b", "a"]
    table = StaticRangeInversions(iter(values))
    assert table.query(0, 4) == 4
    assert len(table) == 4
    assert table.tolist() == values
    assert str(table) == str(values)
    assert repr(table) == "StaticRangeInversions(%r)" % values
    values[0] = "z"
    copy = table.tolist()
    copy[0] = "z"
    assert table.tolist()[0] == "c"
    assert table.query(0, 4) == 4
    empty = StaticRangeInversions([])
    assert empty.query(0, 0) == 0
    assert empty.tolist() == []
    for width in (0, -1):
        with pytest.raises(ValueError):
            StaticRangeInversions([], width)
    for left, right in ((-1, 1), (1, 0), (0, 5)):
        with pytest.raises(IndexError):
            table.query(left, right)


def test_matches_offline_inversions():
    from library_codex.range_query.OfflineRangeInversions import range_inversions

    rng = random.Random(290178)
    for n in range(100):
        values = [rng.randrange(-4, 5) for _ in range(n)]
        queries = []
        for _ in range(100):
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            queries.append((left, right))
        rng.shuffle(queries)
        table = StaticRangeInversions(values)
        assert range_inversions(values, queries) == [table.query(l, r) for l, r in queries]
    assert range_inversions([], []) == []
