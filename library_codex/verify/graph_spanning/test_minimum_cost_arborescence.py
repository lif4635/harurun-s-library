import itertools
import random
import pytest

from library_codex.graph_spanning.MinimumCostArborescence import minimum_cost_arborescence


def _is_arborescence(n, root, edges, selected):
    if len(selected) != n - 1:
        return False
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for edge_id in selected:
        u, v, _ = edges[edge_id]
        graph[u].append(v)
        indegree[v] += 1
    if indegree[root] or any(indegree[v] != 1 for v in range(n) if v != root):
        return False
    seen = {root}
    stack = [root]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return len(seen) == n


def test_minimum_cost_arborescence_against_edge_subsets():
    rng = random.Random(14)
    for n in range(1, 7):
        for _ in range(500):
            root = rng.randrange(n)
            possible = [(u, v) for u in range(n) for v in range(n) if u != v]
            rng.shuffle(possible)
            edge_count = rng.randrange(min(10, len(possible)) + 1)
            edges = [(u, v, rng.randrange(-8, 12))
                     for u, v in possible[:edge_count]]
            if edges and rng.randrange(3) == 0:
                u, v, _ = rng.choice(edges)
                edges.append((u, v, rng.randrange(-8, 12)))
            expected = float("inf")
            for selected in itertools.combinations(range(len(edges)), n - 1):
                if _is_arborescence(n, root, edges, selected):
                    expected = min(expected,
                                   sum(edges[i][2] for i in selected))
            result = minimum_cost_arborescence(n, root, edges)
            if expected == float("inf"):
                assert result is None
            else:
                value, selected = result
                assert value == expected
                assert _is_arborescence(n, root, edges, selected)


def test_nested_cycles_and_deep_path():
    n = 30000
    edges = [(2, 1, 0), (1, 2, 0), (0, 1, n)]
    for vertex in range(3, n):
        edges.extend(((vertex, 1, vertex - 2), (1, vertex, 0)))
    value, selected = minimum_cost_arborescence(n, 0, edges)
    assert value == n
    assert _is_arborescence(n, 0, edges, selected)
    edges = [(i, i + 1, -1) for i in range(n - 1)]
    assert minimum_cost_arborescence(n, 0, edges) == (1 - n, list(range(n - 1)))


def test_empty_loops_unreachable_and_input_preservation():
    assert minimum_cost_arborescence(0, 0, []) == (0, [])
    assert minimum_cost_arborescence(1, 0, [(0, 0, -10)]) == (0, [])
    assert minimum_cost_arborescence(3, 0, [(1, 2, -1), (2, 1, -1)]) is None
    edges = [(0, 1, 8), (0, 1, -3), (1, 1, -100), (1, 0, -100)]
    before = edges[:]
    assert minimum_cost_arborescence(2, 0, edges) == (-3, [1])
    assert edges == before
    with pytest.raises(IndexError):
        minimum_cost_arborescence(2, 2, [])
