import random

import pytest

from library_codex.tree.DSUOnTree import DSUOnTree
from library_codex.benchmarks.dsu_on_tree import Baseline, make_tree


def test_dsu_on_tree_subtree_distinct_colors():
    rng = random.Random(271605)
    for size in range(1, 100):
        tree = make_tree(size, "random", size)
        colors = [rng.randrange(15) for _ in range(size)]
        root = rng.randrange(size)
        solver = DSUOnTree(tree, root)
        count = [0] * 15
        distinct = [0]
        answer = [0] * size

        def add(vertex):
            color = colors[vertex]
            if count[color] == 0:
                distinct[0] += 1
            count[color] += 1

        def remove(vertex):
            color = colors[vertex]
            count[color] -= 1
            if count[color] == 0:
                distinct[0] -= 1

        def query(vertex):
            answer[vertex] = distinct[0]

        solver.run(add, query, remove)
        for vertex in range(size):
            subtree = solver.euler[solver.down[vertex] : solver.up[vertex]]
            assert answer[vertex] == len({colors[node] for node in subtree})


@pytest.mark.parametrize("cls", [DSUOnTree, Baseline])
def test_subtree_membership_reset_and_repeated_run(cls):
    rng = random.Random(99372)
    for n in range(1, 130):
        tree = make_tree(n, "random", n)
        for edges in tree:
            rng.shuffle(edges)
        original = [row[:] for row in tree]
        root = rng.randrange(n)
        solver = cls(tree, root)
        parent = [-1] * n
        order = [root]
        for v in order:
            for u in tree[v]:
                if u != parent[v]:
                    parent[u] = v
                    order.append(u)
        expected = [{v} for v in range(n)]
        for v in reversed(order[1:]):
            expected[parent[v]].update(expected[v])
        for _ in range(2):
            active = set()
            visited = []
            calls = [0, 0]

            def add(v):
                assert v not in active
                active.add(v)
                calls[0] += 1

            def remove(v):
                active.remove(v)
                calls[1] += 1

            def query(v):
                assert active == expected[v]
                visited.append(v)

            def reset():
                assert not active

            assert solver.run(add, query, remove, reset) is None
            assert sorted(visited) == list(range(n))
            assert active == set(range(n))
            assert calls[0] - calls[1] == n
            assert calls[0] <= n * n.bit_length()
        for v in range(n):
            assert set(solver.euler[solver.down[v]:solver.up[v]]) == expected[v]
            assert solver.euler[solver.index(v)] == v
        assert tree == original


@pytest.mark.parametrize("cls", [DSUOnTree, Baseline])
def test_deep_chain_and_invalid_input(cls):
    n = 100000
    solver = cls(make_tree(n, "chain", 0))
    total = [0]
    answers = [0] * n

    def add(v):
        total[0] += 1

    def query(v):
        answers[v] = total[0]

    def remove(v):
        pytest.fail("chain must not remove a vertex")

    solver.run(add, query, remove)
    assert answers == list(range(n, 0, -1))
    with pytest.raises(IndexError):
        cls([])
    with pytest.raises(ValueError):
        cls([[], []])
    with pytest.raises(ValueError):
        cls([[1, 2], [0, 2], [0, 1]])
