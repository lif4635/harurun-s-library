import random

import pytest

from library_codex.tree.TreePathCompositeSum import TreePathCompositeSum


def naive(values, edges, root, mod):
    graph = [[] for _ in values]
    for u, v, b, c in edges:
        graph[u].append((v, b, c))
        graph[v].append((u, b, c))
    total = 0
    stack = [(root, -1, 1, 0)]
    while stack:
        v, p, a, d = stack.pop()
        total += a * values[v] + d
        for u, b, c in graph[v]:
            if u != p:
                stack.append((u, v, a * b % mod, (a * c + d) % mod))
    return total % mod


def test_random_updates_and_roots():
    rng = random.Random(9317)
    for mod in (1, 12, 998244353):
        for n in (1, 2, 5, 30, 100):
            for shape in ("path", "star", "random"):
                labels = list(range(n))
                rng.shuffle(labels)
                edges = []
                for i in range(1, n):
                    p = i - 1 if shape == "path" else 0 if shape == "star" else rng.randrange(i)
                    u, v = labels[p], labels[i]
                    if rng.randrange(2):
                        u, v = v, u
                    edges.append((u, v, rng.randrange(mod), rng.randrange(mod)))
                rng.shuffle(edges)
                values = [rng.randrange(mod) for _ in range(n)]
                tree = TreePathCompositeSum(values, edges, mod)
                for _ in range(150):
                    if n == 1 or rng.randrange(2):
                        v, x = rng.randrange(n), rng.randrange(-mod, mod + 1)
                        tree.set(v, x)
                        values[v] = x % mod
                    else:
                        e = rng.randrange(n - 1)
                        b, c = rng.randrange(-mod, mod + 1), rng.randrange(-mod, mod + 1)
                        tree.set_edge(e, b, c)
                        u, v, _, _ = edges[e]
                        edges[e] = u, v, b % mod, c % mod
                    root = rng.randrange(n)
                    assert tree.query(root) == naive(values, edges, root, mod)
                assert tree.tolist() == values
                assert tree.edges() == edges
                assert str(tree) == str((values, edges))
                assert repr(tree) == "TreePathCompositeSum(%r, %r, mod=%r)" % (values, edges, mod)
                for root in range(n):
                    assert tree.query(root) == naive(values, edges, root, mod)


def test_invalid_inputs_and_copies():
    with pytest.raises(ValueError):
        TreePathCompositeSum([], [])
    with pytest.raises(ValueError):
        TreePathCompositeSum([1], [], 0)
    with pytest.raises(ValueError):
        TreePathCompositeSum([1, 2], [])
    with pytest.raises(ValueError):
        TreePathCompositeSum([1, 2, 3], [(0, 1, 1, 0), (0, 1, 1, 0)])
    with pytest.raises(IndexError):
        TreePathCompositeSum([1, 2], [(0, 2, 1, 0)])
    tree = TreePathCompositeSum([2, 3], [(0, 1, 2, 1)])
    for index in (-1, 2):
        with pytest.raises(IndexError):
            tree.set(index, 3)
        with pytest.raises(IndexError):
            tree.query(index)
    for index in (-1, 1):
        with pytest.raises(IndexError):
            tree.set_edge(index, 1, 0)
    tree.tolist()[0] = 100
    tree.edges()[0] = (0, 1, 0, 0)
    assert tree.query(0) == 9
    assert tree.query(1) == 8


def test_deep_tree_and_lightweight_storage():
    n = 20000
    tree = TreePathCompositeSum([1] * n, [(i - 1, i, 1, 0) for i in range(1, n)])
    assert len(tree._a) == 2 * n - 1
    for root in (0, n // 2, n - 1):
        assert tree.query(root) == n
    tree.set(n - 1, 5)
    tree.set_edge(n // 2, 0, 7)
    assert tree.query(0) == n // 2 + 1 + 7 * (n - n // 2 - 1)
    assert len(tree._a) == 2 * n - 1
