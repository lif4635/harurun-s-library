import itertools
import random

import pytest

from library_codex.union_find.PotentialUnionFind import PotentialUnionFind


def test_additive_constraints():
    tree = PotentialUnionFind(5, lambda a, b: (a + b) % 7, lambda a: -a % 7, 0)
    assert tree.diff(0, 1) is None
    assert tree.merge(0, 1, 5)
    assert tree.merge(1, 2, 4)
    assert tree.diff(0, 2) == 2
    assert tree.diff(2, 0) == 5
    assert tree.merge(0, 2, 2)
    assert not tree.merge(0, 2, 3)
    assert tree.merge(3, 2, 1)
    assert tree.diff(3, 0) == 6
    assert tree.size(3) == 4
    assert tree.component_count == 2
    assert tree.same(0, 3)
    assert not tree.same(0, 4)


def test_noncommutative_random_constraints():
    rng = random.Random(291734)
    unit = (0, 1, 2, 3)
    permutations = list(itertools.permutations(unit))

    def op(a, b):
        return tuple(a[b[i]] for i in range(4))

    def inv(a):
        result = [0] * 4
        for i, value in enumerate(a):
            result[value] = i
        return tuple(result)

    for n in (1, 2, 3, 10, 40):
        tree = PotentialUnionFind(n, op, inv, unit)
        graph = [[] for _ in range(n)]

        def difference(first, second):
            values = {first: unit}
            queue = [first]
            for node in queue:
                for neighbor, value in graph[node]:
                    if neighbor not in values:
                        values[neighbor] = op(values[node], value)
                        queue.append(neighbor)
            return values.get(second), len(values)

        for step in range(1000):
            first, second = rng.randrange(n), rng.randrange(n)
            expected, size = difference(first, second)
            if step % 3:
                value = rng.choice(permutations)
                accepted = expected is None or expected == value
                assert tree.merge(first, second, value) == accepted
                if accepted:
                    graph[first].append((second, value))
                    graph[second].append((first, inv(value)))
            else:
                assert tree.diff(first, second) == expected
                assert tree.same(first, second) == (expected is not None)
                assert tree.size(first) == size
            if step % 67 == 0:
                rows = tree.tolist()
                assert str(tree) == str(rows)
                assert repr(tree) == "PotentialUnionFind(%r)" % rows
                for vertex, (root, value) in enumerate(rows):
                    assert difference(root, vertex)[0] == value
                    assert tree.weight(vertex) == value
                    assert tree.find(vertex) == root
                assert tree.component_count == len({row[0] for row in rows})


def test_empty_and_invalid_size():
    tree = PotentialUnionFind(0, lambda a, b: a + b, lambda a: -a, 0)
    assert tree.tolist() == []
    assert tree.component_count == 0
    with pytest.raises(ValueError):
        PotentialUnionFind(-1, lambda a, b: a + b, lambda a: -a, 0)
