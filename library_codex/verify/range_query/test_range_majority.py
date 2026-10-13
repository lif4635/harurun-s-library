from collections import Counter
import random

import pytest

from library_codex.range_query.RangeMajority import RangeMajority


def expected(values, left, right):
    return next(((value, count) for value, count in Counter(values[left:right]).items()
                 if count * 2 > right - left), None)


def check_forest(table):
    values = table.tolist()
    seen = set()
    for value, root in table._roots.items():
        assert table._parent[root] == -1
        stack = [(root, -1, table.n)]
        while stack:
            node, lower, upper = stack.pop()
            assert node not in seen and lower < node < upper
            seen.add(node)
            assert values[node] == value
            size = 1
            for child, lo, hi in ((table._left[node], lower, node), (table._right[node], node, upper)):
                if child >= 0:
                    assert table._parent[child] == node
                    assert table._priority[node] <= table._priority[child]
                    size += table._sizes[child]
                    stack.append((child, lo, hi))
            assert table._sizes[node] == size
    assert len(seen) == table.n


def test_static_majority_random():
    rng = random.Random(871246)
    for n in range(100):
        values = [rng.randrange(12) for _ in range(n)]
        table = RangeMajority(values)
        for _ in range(200):
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            assert table.majority(left, right) == expected(values, left, right)
        assert table._roots is None


def test_dynamic_majority_random_and_node_reuse(monkeypatch):
    rng = random.Random(71539)
    monkeypatch.setattr("library_codex.range_query.RangeMajority.getrandbits", random.Random(9183).getrandbits)
    choices = [None, "a", "b", -1, 0, 2, (1, 2)]
    for n in (1, 2, 3, 7, 16, 31, 80):
        values = [rng.choice(choices) for _ in range(n)]
        table = RangeMajority(values)
        for step in range(1200):
            if step % 3:
                index, value = rng.randrange(n), rng.choice(choices)
                table.set(index, value)
                values[index] = value
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            value = rng.choice(choices)
            count = values[left:right].count(value)
            assert table.majority(left, right) == expected(values, left, right)
            assert table.count(value, left, right) == count
            assert table.is_majority(value, left, right) == (count * 2 > right - left)
            if step % 50 == 0 and table._roots is not None:
                check_forest(table)
                assert all(len(array) == n for array in (table._left, table._right, table._parent, table._sizes, table._priority))
        assert table.tolist() == values
        assert str(table) == str(values)
        assert repr(table) == "RangeMajority(%r)" % values
        snapshot = table.tolist()
        snapshot.clear()
        assert table.tolist() == values


def test_majority_boundaries_and_noop_updates():
    table = RangeMajority([None, None, 1, 2])
    table.set(0, None)
    assert table._roots is None
    assert table.majority(0, 4) is None
    table.set(3, None)
    assert table.majority(0, 4) == (None, 3)
    for i in range(4):
        table.set(i, 7)
    check_forest(table)
    assert set(table._roots) == {7}
    assert table.majority(0, 4) == (7, 4)
    for index in (-1, 4):
        with pytest.raises(IndexError):
            table.set(index, 0)
    with pytest.raises(TypeError):
        table.set(0, [])
    assert table.tolist() == [7] * 4
    for left, right in ((-1, 2), (0, 5), (2, 1)):
        with pytest.raises(IndexError):
            table.majority(left, right)
        with pytest.raises(IndexError):
            table.count(7, left, right)
    empty = RangeMajority([])
    assert empty.majority(0, 0) is None
    with pytest.raises(IndexError):
        empty.set(0, 1)


def test_majority_equal_priorities_and_changing_value_set(monkeypatch):
    monkeypatch.setattr("library_codex.range_query.RangeMajority.getrandbits", lambda bits: 0)
    table = RangeMajority([0] * 300)
    for i in range(300):
        table.set(i, i + 1)
    check_forest(table)
    assert len(table._roots) == 300
    assert table.majority(0, 300) is None
    for i in reversed(range(300)):
        table.set(i, -1)
    check_forest(table)
    assert table.majority(0, 300) == (-1, 300)
    assert table.count(-1, 70, 260) == 190
    assert len(table._roots) == 1
