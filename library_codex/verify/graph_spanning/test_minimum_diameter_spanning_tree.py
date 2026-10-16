import itertools
import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph_spanning.MinimumDiameterSpanningTree import minimum_diameter_spanning_tree


def diameter(n, edges, ids):
    if len(ids) != max(0, n - 1) or len(set(ids)) != len(ids):
        return None
    graph = [[] for _ in range(n)]
    for eid in ids:
        u, v, weight = edges[eid]
        graph[u].append((v, weight))
        graph[v].append((u, weight))
    result = 0
    for root in range(n):
        dist = [None] * n
        dist[root] = 0
        queue = [root]
        for u in queue:
            for v, weight in graph[u]:
                if dist[v] is None:
                    dist[v] = dist[u] + weight
                    queue.append(v)
        if len(queue) != n:
            return None
        result = max(result, max(dist))
    return result


def brute(n, edges):
    best = None
    for ids in itertools.combinations(range(len(edges)), max(0, n - 1)):
        value = diameter(n, edges, ids)
        if value is not None and (best is None or value < best):
            best = value
    return best


def test_random_against_all_spanning_trees():
    rng = random.Random(163)
    for n in range(1, 7):
        for _ in range(120):
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(8))
                     for _ in range(rng.randrange(11))]
            original = edges[:]
            expected = brute(n, edges)
            actual = minimum_diameter_spanning_tree(n, edges)
            assert edges == original
            if expected is None:
                assert actual is None
            else:
                value, ids = actual
                assert value == expected
                assert ids == sorted(ids)
                assert diameter(n, edges, ids) == value


def test_empty_singleton_disconnected():
    assert minimum_diameter_spanning_tree(0, []) == (0, [])
    assert minimum_diameter_spanning_tree(1, [(0, 0, 7)]) == (0, [])
    assert minimum_diameter_spanning_tree(3, [(0, 1, 0)]) is None


def test_half_integral_center_and_parallel_edges():
    edges = [(0, 1, 99), (0, 1, 3), (1, 2, 2), (2, 3, 4)]
    assert minimum_diameter_spanning_tree(4, edges) == (9, [1, 2, 3])
    assert minimum_diameter_spanning_tree(3, [(0, 1, 0), (1, 2, 0), (0, 2, 0)])[0] == 0


def test_large_integer_weights():
    edges = [(0, 1, 10 ** 50), (1, 2, 10 ** 50 + 1), (0, 2, 10 ** 50 + 2)]
    value, ids = minimum_diameter_spanning_tree(3, edges)
    assert value == 2 * 10 ** 50 + 1
    assert diameter(3, edges, ids) == value


def test_invalid_input():
    for n, edges in [(-1, []), (2, [(0, 1, -1)]), (2, [(0, 2, 1)]), (0, [(0, 0, 0)])]:
        with pytest.raises(ValueError):
            minimum_diameter_spanning_tree(n, edges)
