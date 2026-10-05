import random
from itertools import product

import pytest

from library_codex.segment_tree.RangeLinearAddRangeMin import RangeLinearAddRangeMin


def test_range_linear_add_range_min_against_brute_force():
    rng = random.Random(202407)
    for size in range(1, 70):
        values = [rng.randrange(-1000, 1001) for _ in range(size)]
        tree = RangeLinearAddRangeMin(values)
        for _ in range(800):
            left = rng.randrange(size)
            right = rng.randrange(left + 1, size + 1)
            if rng.randrange(3):
                slope = rng.randrange(-100, 101)
                intercept = rng.randrange(-1000, 1001)
                tree.add(left, right, slope, intercept)
                for index in range(left, right):
                    values[index] += slope * index + intercept
            else:
                assert tree.query(left, right) == min(values[left:right])


def test_all_small_ranges_and_debug():
    for n in range(1, 6):
        for values in product((-2, 0, 3), repeat=n):
            expected = list(values)
            tree = RangeLinearAddRangeMin(iter(values))
            for left in range(n):
                for right in range(left + 1, n + 1):
                    slope, intercept = (left + right) % 5 - 2, 2 - right
                    tree.add(left, right, slope, intercept)
                    for i in range(left, right):
                        expected[i] += slope * i + intercept
                    assert tree.tolist() == expected
                    assert str(tree) == str(expected)
                    assert repr(tree) == "RangeLinearAddRangeMin(%r)" % expected
                    for a in range(n):
                        for b in range(a + 1, n + 1):
                            assert tree.query(a, b) == min(expected[a:b])


def test_huge_values_empty_and_invalid():
    huge = 10**100
    values = [huge, -huge, huge + 1, 2 * huge, 7]
    tree = RangeLinearAddRangeMin(values)
    tree.add(0, 5, -huge, huge)
    expected = [value + huge * (1 - i) for i, value in enumerate(values)]
    tree.add(3, 3, huge, huge)
    tree.add(0, 5, 0, 0)
    assert tree.tolist() == expected
    for left in range(5):
        for right in range(left + 1, 6):
            assert tree.query(left, right) == min(expected[left:right])
    empty = RangeLinearAddRangeMin([])
    empty.add(0, 0, 5, 9)
    assert empty.tolist() == []
    with pytest.raises(IndexError):
        empty.query(0, 0)
    for left, right in [(-1, 2), (2, 1), (0, 6)]:
        with pytest.raises(IndexError):
            tree.add(left, right, 1, 2)
        with pytest.raises(IndexError):
            tree.query(left, right)
