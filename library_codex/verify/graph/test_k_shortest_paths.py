import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.KShortestPaths import (  # noqa: E402
    KShortestPathDirected,
    KShortestPathUndirected,
    k_shortest_paths_directed,
    k_shortest_paths_undirected,
)


def _all_simple_paths(n, edges, source, target, directed):
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        graph[u].append((v, weight, edge_id))
        if not directed:
            graph[v].append((u, weight, edge_id))
    result = []
    stack = [(source, 1 << source, 0, [source], [])]
    while stack:
        v, used, cost, vertices, edge_ids = stack.pop()
        if v == target:
            result.append((cost, vertices, edge_ids))
            continue
        for to, weight, edge_id in graph[v]:
            if not used >> to & 1:
                stack.append((to, used | 1 << to, cost + weight,
                              vertices + [to], edge_ids + [edge_id]))
    result.sort(key=lambda item: (item[0], item[2]))
    return result


def _validate_paths(n, edges, source, target, directed, paths):
    for cost, vertices, edge_ids in paths:
        assert vertices[0] == source and vertices[-1] == target
        assert len(vertices) == len(set(vertices))
        assert len(edge_ids) + 1 == len(vertices)
        assert cost == sum(edges[e][2] for e in edge_ids)
        for i, edge_id in enumerate(edge_ids):
            u, v, _ = edges[edge_id]
            if directed:
                assert (vertices[i], vertices[i + 1]) == (u, v)
            else:
                assert {vertices[i], vertices[i + 1]} == {u, v}


def test_k_shortest_directed_against_all_simple_paths():
    rng = random.Random(20)
    for n in range(1, 8):
        possible = [(u, v) for u in range(n) for v in range(n) if u != v]
        for _ in range(250):
            rng.shuffle(possible)
            edges = [(u, v, rng.randrange(8))
                     for u, v in possible[:rng.randrange(min(12, len(possible)) + 1)]]
            source = rng.randrange(n)
            target = rng.randrange(n)
            k = rng.randrange(1, 15)
            expected = _all_simple_paths(n, edges, source, target, True)[:k]
            actual = k_shortest_paths_directed(n, edges, source, target, k)
            _validate_paths(n, edges, source, target, True, actual)
            assert [x[0] for x in actual] == [x[0] for x in expected]
            assert len(actual) == len(expected)


def test_k_shortest_undirected_parallel_against_all_simple_paths():
    rng = random.Random(21)
    for n in range(1, 8):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(250):
            rng.shuffle(possible)
            edges = [(u, v, rng.randrange(8))
                     for u, v in possible[:rng.randrange(min(10, len(possible)) + 1)]]
            if edges and rng.randrange(3) == 0:
                u, v, _ = rng.choice(edges)
                edges.append((u, v, rng.randrange(8)))
            source = rng.randrange(n)
            target = rng.randrange(n)
            k = rng.randrange(1, 15)
            expected = _all_simple_paths(n, edges, source, target, False)[:k]
            actual = k_shortest_paths_undirected(n, edges, source, target, k)
            _validate_paths(n, edges, source, target, False, actual)
            assert [x[0] for x in actual] == [x[0] for x in expected]
            assert len(actual) == len(expected)


def test_incremental_wrappers():
    directed = KShortestPathDirected(4, 0, 3)
    undirected = KShortestPathUndirected(4, 0, 3)
    edges = [(0, 1, 1), (1, 3, 1), (0, 2, 2), (2, 3, 1), (1, 2, 1)]
    for edge in edges:
        directed.add_edge(*edge)
        undirected.add_edge(*edge)
    expected = directed.solve(20)
    actual = []
    while True:
        item = directed.get_next_smallest()
        if item is None:
            break
        actual.append(item)
    assert actual == expected
    expected = undirected.solve(20)
    actual = []
    while True:
        item = undirected.get_next_smallest()
        if item is None:
            break
        actual.append(item)
    assert actual == expected
