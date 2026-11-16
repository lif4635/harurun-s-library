import random

import pytest

from library_codex.ordered_set.IntervalMap import IntervalMap


def compressed(values):
    result = []
    for point in sorted(values):
        value = values[point]
        if result and result[-1][1] == point and result[-1][2] == value:
            result[-1] = result[-1][0], point + 1, value
        else:
            result.append((point, point + 1, value))
    return result


def test_random_assign_erase_get_items():
    rng = random.Random(8931)
    for _ in range(20):
        tree, values = IntervalMap(), {}
        missing = object()
        for _ in range(400):
            left, right = sorted((rng.randrange(-30, 31), rng.randrange(-30, 31)))
            if rng.randrange(3):
                value = rng.choice([None, [1], [2], [3]])
                tree.assign(left, right, value)
                for i in range(left, right):
                    values[i] = value
            else:
                removed = sum(i in values for i in range(left, right))
                assert tree.erase(left, right) == removed
                for i in range(left, right):
                    values.pop(i, None)
            assert tree.items() == compressed(values)
            assert tree.items(left, right) == compressed({i: v for i, v in values.items() if left <= i < right})
            assert tree.items(right=right) == compressed({i: v for i, v in values.items() if i < right})
            assert tree.items(left=left) == compressed({i: v for i, v in values.items() if left <= i})
            assert tree.covered_length == len(values)
            assert len(tree) == len(compressed(values))
            for point in (left, right, 31):
                assert tree.get(point, missing) == values.get(point, missing)
            assert str(tree) == str(compressed(values))
            assert repr(tree) == "IntervalMap(%r)" % compressed(values)


def test_large_coordinates_and_reclaimed_storage():
    tree = IntervalMap()
    tree.assign(-10**30, 10**30, "a")
    tree.assign(-4, 9, "b")
    assert tree.items() == [(-10**30, -4, "a"), (-4, 9, "b"), (9, 10**30, "a")]
    tree.assign(-4, 9, "a")
    assert tree.items() == [(-10**30, 10**30, "a")]
    assert tree.erase(-10**40, 10**40) == 2 * 10**30
    for i in range(10000):
        tree.assign(0, 1, i)
    assert tree.items() == [(0, 1, 9999)]
    assert len(tree._starts.key) <= 2 * len(tree) + 64
    assert tree.erase(0, 1) == 1
    assert tree.items() == []


def test_empty_and_invalid_ranges():
    tree = IntervalMap()
    tree.assign(0, 0, 3)
    assert tree.erase(0, 0) == 0
    assert tree.items() == []
    for call in (lambda: tree.assign(2, 1, 0), lambda: tree.erase(2, 1), lambda: tree.items(2, 1)):
        with pytest.raises(ValueError):
            call()
