import random

import pytest

from library_codex.graph_flow.DynamicStarMinCut import DynamicStarMinCut


def cut_weight(vertices, edges, weights):
    selected = set(vertices)
    return sum(weights[v] for v in selected) + sum(
        w for u, v, w in edges if (u in selected) != (v in selected)
    )


def naive(edges, weights):
    n = len(weights)
    return min(cut_weight([v for v in range(n) if mask >> v & 1], edges, weights)
               for mask in range(1, 1 << n))


def test_random_updates_and_recovered_cut():
    rng = random.Random(5384)
    for n in range(1, 9):
        for _ in range(25):
            edges = [(u, v, rng.randrange(10)) for u in range(n)
                     for v in range(u) if rng.randrange(3)]
            weights = [rng.randrange(12) for _ in range(n)]
            original = weights[:]
            graph = DynamicStarMinCut(n, edges, weights)
            assert graph.min_cut() == naive(edges, weights)
            assert weights == original
            weights[0] += 100
            assert graph.tolist() == original
            weights[0] -= 100
            for _ in range(15):
                vertex = rng.randrange(n)
                weights[vertex] = rng.randrange(12)
                expected = naive(edges, weights)
                assert graph.set(vertex, weights[vertex]) == expected
                assert graph.min_cut() == expected
                vertices = graph.cut()
                assert vertices and vertices == sorted(set(vertices))
                assert cut_weight(vertices, edges, weights) == expected
                assert graph.tolist() == weights


def test_zero_singleton_huge_and_debug():
    graph = DynamicStarMinCut(1, [])
    assert graph.min_cut() == 0
    assert graph.cut() == [0]
    assert graph.set(0, 10 ** 100) == 10 ** 100
    assert graph.set(0, 7) == 7
    assert str(graph) == "[7]"
    assert repr(graph) == "DynamicStarMinCut([7])"
    values = graph.tolist()
    values[0] = 88
    assert graph.min_cut() == 7
    edges = [(0, 1, 3), (1, 0, 5), (2, 2, 99)]
    graph = DynamicStarMinCut(3, edges, [10, 10, 10])
    assert graph.min_cut() == 10
    assert graph.set(2, 0) == 0


def test_invalid_update_preserves_state():
    graph = DynamicStarMinCut(2, [(0, 1, 5)], [2, 3])
    for vertex in (-1, 2):
        with pytest.raises(IndexError):
            graph.set(vertex, 10)
    with pytest.raises(ValueError):
        graph.set(0, -1)
    assert graph.tolist() == [2, 3]
    assert graph.min_cut() == 5
    for values in ([1], [-1, 2]):
        with pytest.raises(ValueError):
            DynamicStarMinCut(2, [], values)


def test_deep_tree_without_recursion():
    n = 1200
    graph = DynamicStarMinCut(n, [(v - 1, v, 1) for v in range(1, n)])
    assert graph.min_cut() == 0
    assert graph.set(n - 1, 8) == 1
    assert graph.set(0, 8) == 2
