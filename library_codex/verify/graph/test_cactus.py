import random

import pytest

from library_codex.graph_connectivity.Cactus import decompose, is_cactus


def _is_cactus_bruteforce(n, edges):
    if any(u == v for u, v in edges) or len({tuple(sorted(e)) for e in edges}) < len(edges):
        return False
    graph = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        graph[u].append((v, edge_id))
        graph[v].append((u, edge_id))
    for forbidden, (start, goal) in enumerate(edges):
        paths = 0
        stack = [(start, 1 << start)]
        while stack:
            vertex, seen = stack.pop()
            for to, edge_id in graph[vertex]:
                if edge_id == forbidden:
                    continue
                if to == goal:
                    paths += 1
                    if paths >= 2:
                        return False
                elif not seen >> to & 1:
                    stack.append((to, seen | 1 << to))
    return True


def _check_decomposition(n, edges, result):
    cycles, edge_cycle = result
    assert len(edge_cycle) == len(edges)
    seen = set()
    for cycle_id, cycle in enumerate(cycles):
        assert len(cycle) >= 3
        assert all(edge_cycle[edge_id] == cycle_id for edge_id in cycle)
        assert not (seen & set(cycle))
        seen.update(cycle)
        degree = {}
        for edge_id in cycle:
            u, v = edges[edge_id]
            degree[u] = degree.get(u, 0) + 1
            degree[v] = degree.get(v, 0) + 1
        assert len(degree) == len(cycle)
        assert set(degree.values()) == {2}
    assert seen == {edge_id for edge_id, value in enumerate(edge_cycle) if value >= 0}


def test_random_against_path_count_definition():
    random.seed(20260815)
    for n in range(1, 8):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(350):
            edges = [edge for edge in possible if random.randrange(5) == 0]
            expected = _is_cactus_bruteforce(n, edges)
            assert is_cactus(n, edges) == expected
            result = decompose(n, edges)
            assert (result is not None) == expected
            if result is not None:
                _check_decomposition(n, edges, result)


def test_known_graphs_and_invalid_input():
    figure_eight = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)]
    assert is_cactus(5, figure_eight)
    assert not is_cactus(4, [(0, 1), (1, 3), (0, 2), (2, 3), (0, 3)])
    assert not is_cactus(2, [(0, 1), (1, 0)])
    assert not is_cactus(1, [(0, 0)])
    with pytest.raises(IndexError):
        decompose(2, [(0, 2)])
    with pytest.raises(ValueError):
        decompose(-1, [])
