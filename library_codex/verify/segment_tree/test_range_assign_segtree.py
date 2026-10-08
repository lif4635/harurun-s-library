import random

import pytest

from library_codex.segment_tree.RangeAssignSegTree import RangeAssignSegTree


def test_assign_sum_against_array():
    rng = random.Random(81097)
    for n in (0, 1, 2, 3, 7, 16, 17, 63, 64, 65):
        values = [rng.randrange(-20, 21) for _ in range(n)]
        tree = RangeAssignSegTree(lambda a, b: a + b, 0, values)
        assert len(tree) == n
        for step in range(400):
            left, right = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
            if step % 3:
                value = rng.randrange(-20, 21)
                tree.assign(left, right, value)
                values[left:right] = [value] * (right - left)
            else:
                assert tree.prod(left, right) == sum(values[left:right])
            assert tree.all_prod() == sum(values)
            if step % 37 == 0:
                assert tree.tolist() == values
                assert str(tree) == str(values)
                assert repr(tree) == "RangeAssignSegTree(" + str(values) + ")"
        copied = tree.tolist()
        copied.clear()
        assert tree.tolist() == values


def test_noncommutative_affine_and_point_updates():
    rng = random.Random(62713)
    mod = 101

    def op(first, second):
        a, b = first
        c, d = second
        return a * c % mod, (b * c + d) % mod

    for n in (1, 3, 17, 32, 63):
        values = [(1, 0)] * n
        tree = RangeAssignSegTree(op, (1, 0), iter(values))
        for step in range(500):
            left = rng.randrange(n)
            right = rng.randrange(left + 1, n + 1)
            value = rng.randrange(mod), rng.randrange(mod)
            if step % 4 == 0:
                tree.assign(left, right, value)
                values[left:right] = [value] * (right - left)
            elif step % 4 == 1:
                tree.set(left, value)
                values[left] = value
            elif step % 4 == 2:
                tree.add(left, value)
                values[left] = op(value, values[left])
            expected = (1, 0)
            for item in values[left:right]:
                expected = op(expected, item)
            assert tree.prod(left, right) == expected
            assert tree.get(left) == values[left]
        assert tree.tolist() == values


def test_none_values_empty_ranges_and_validation():
    op = lambda a, b: b if a is None else a
    tree = RangeAssignSegTree(op, None, 3)
    tree.assign(0, 3, 7)
    tree.assign(0, 2, None)
    assert tree.tolist() == [None, None, 7]
    assert tree.prod(1, 1) is None
    assert tree.prod(0, 3) == 7
    for left, right in ((-1, 1), (1, 4), (2, 1)):
        with pytest.raises(IndexError):
            tree.assign(left, right, 0)
        with pytest.raises(IndexError):
            tree.prod(left, right)
    for index in (-1, 3):
        with pytest.raises(IndexError):
            tree.get(index)
        with pytest.raises(IndexError):
            tree.set(index, 0)
    with pytest.raises(ValueError):
        RangeAssignSegTree(op, None, -1)


def test_power_tags_keep_only_reachable_prefixes():
    n = 1024
    tree = RangeAssignSegTree(lambda a, b: a + b, 0, n)
    for i in range(0, n, 2):
        tree.assign(i, n, i + 1)
    seen = set()
    for node, tag in enumerate(tree.lazy[1:], 1):
        depth = 0
        while tag is not None:
            seen.add(id(tag))
            tag = tag[1]
            depth += 1
        assert depth <= tree.log + 2 - node.bit_length()
    assert len(seen) <= 2 * n
    assert tree.tolist() == [i // 2 * 2 + 1 for i in range(n)]
