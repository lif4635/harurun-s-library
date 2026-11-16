import random

import pytest

from library_codex.spatial_structure.PrioritySearchTree import PrioritySearchTree


def check_invariants(tree, xs, ys):
    heap, positions = tree._heap, tree._position
    seen = set()
    stack = [(1, 0, tree._base)]
    while stack:
        v, left, right = stack.pop()
        i = heap[v]
        if i >= 0:
            assert i not in seen and ys[i] is not None
            assert positions[i] == v
            assert left <= tree._rank[i] < right
            seen.add(i)
        if v < tree._base:
            for child in (v * 2, v * 2 + 1):
                j = heap[child]
                if j >= 0:
                    assert i >= 0 and (ys[i], i) <= (ys[j], j)
            middle = (left + right) // 2
            stack.extend(((v * 2, left, middle), (v * 2 + 1, middle, right)))
    expected = [(i, x, y) for i, (x, y) in enumerate(zip(xs, ys)) if y is not None]
    assert seen == {i for i, y in enumerate(ys) if y is not None}
    assert tree.items() == expected and len(tree) == len(expected)
    assert str(tree) == str(expected)
    assert repr(tree) == "PrioritySearchTree(%r)" % expected
    assert [tree.get(i) for i in range(len(xs))] == ys


def test_random_updates_reports_and_minima():
    rng = random.Random(34821)
    for n in (0, 1, 2, 3, 7, 16, 31, 64):
        xs = [rng.randrange(-10, 11) for _ in range(n)]
        ys = [rng.choice([None, -4, 0, 3, 7]) for _ in range(n)]
        tree = PrioritySearchTree(xs, ys)
        for _ in range(250):
            if n and rng.randrange(2):
                i = rng.randrange(n)
                if rng.randrange(3):
                    y = rng.choice([None, rng.randrange(-20, 21)])
                    tree.set(i, y)
                    ys[i] = y
                else:
                    assert tree.erase(i) == (ys[i] is not None)
                    ys[i] = None
            left, right = sorted((rng.randrange(-15, 16), rng.randrange(-15, 16)))
            upper = rng.randrange(-25, 26)
            expected = [i for i in range(n) if ys[i] is not None and left <= xs[i] < right]
            assert sorted(tree.report(left, right, upper)) == [i for i in expected if ys[i] < upper]
            assert tree.min_y(left, right) == (min(expected, key=lambda i: (ys[i], i)) if expected else None)
            check_invariants(tree, xs, ys)


def test_ties_boundaries_copy_and_invalid_inputs():
    xs, ys = [2, 2, 3, -1], [5, 5, 5, 5]
    tree = PrioritySearchTree(xs, ys)
    xs[0], ys[0] = 999, 999
    assert tree.min_y(2, 3) == 0
    assert tree.report(2, 3, 5) == []
    assert sorted(tree.report(2, 3, 6)) == [0, 1]
    tree.erase(0)
    assert tree.min_y(2, 3) == 1
    for i in (-1, 4):
        for call in (lambda: tree.set(i, 0), lambda: tree.erase(i), lambda: tree.get(i)):
            with pytest.raises(IndexError):
                call()
    for call in (lambda: tree.min_y(3, 2), lambda: tree.report(3, 2, 6), lambda: PrioritySearchTree([1], [])):
        with pytest.raises(ValueError):
            call()


def test_monotone_points_and_repeated_reactivation():
    n = 10000
    tree = PrioritySearchTree(range(n), range(n))
    assert sorted(tree.report(0, n, n)) == list(range(n))
    for i in range(n):
        tree.set(i, -i)
    assert tree.min_y(0, n) == n - 1
    for i in range(n):
        assert tree.erase(i)
    assert tree.report(0, n, n) == [] and tree.items() == []
    for i in range(n):
        tree.set(i, i)
    assert tree.min_y(500, 900) == 500
    assert len(tree._heap) == 2 * tree._base
    assert len(tree._position) == n


def test_initially_inactive_and_comparable_values():
    tree = PrioritySearchTree(["a", "b", "b"])
    assert len(tree) == 0 and tree.min_y("a", "c") is None
    tree.set(2, "low")
    tree.set(1, "high")
    assert tree.min_y("a", "c") == 1
    assert sorted(tree.report("a", "c", "z")) == [1, 2]
    tree.set(1, None)
    assert tree.min_y("b", "c") == 2
    tree.set(1, "low")
    assert tree.min_y("b", "c") == 1
    assert tree.report("b", "c", "low") == []

