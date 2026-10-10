import itertools
import random

import pytest

from library_codex.graph_connectivity.TreeDecompositionWidth2 import tree_decomposition_width2


def _possible(n, edges):
    initial = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            initial[u].add(v)
            initial[v].add(u)
    for order in itertools.permutations(range(n)):
        graph = [row.copy() for row in initial]
        for v in order:
            neighbors = list(graph[v])
            if len(neighbors) > 2:
                break
            for u in neighbors:
                graph[u].remove(v)
            if len(neighbors) == 2:
                u, w = neighbors
                graph[u].add(w)
                graph[w].add(u)
        else:
            return True
    return False


def _check(n, edges, result):
    bags, parent = result
    assert len(bags) == len(parent) == n
    contained = [[] for _ in range(n)]
    covered = set()
    for i, bag in enumerate(bags):
        assert 1 <= len(bag) <= 3
        assert len(set(bag)) == len(bag)
        for v in bag:
            contained[v].append(i)
        for u in bag:
            for v in bag:
                covered.add((u, v))
        assert i < parent[i] < n if i + 1 < n else parent[i] == -1
    assert all((u, v) in covered for u, v in edges)
    for ids in contained:
        assert ids
        nodes = set(ids)
        assert sum(parent[i] in nodes for i in ids) == len(ids) - 1


def test_width2_against_elimination_orders():
    rng = random.Random(805311)
    for n in range(7):
        possible_edges = list(itertools.combinations(range(n), 2))
        for _ in range(90):
            edges = [e for e in possible_edges if rng.randrange(3) == 0]
            before = edges[:]
            result = tree_decomposition_width2(n, edges)
            assert (result is not None) == _possible(n, edges)
            assert edges == before
            if result is not None:
                _check(n, edges, result)


def test_width2_parallel_loops_disconnected_and_k4():
    edges = [(0, 1), (1, 0), (0, 0), (1, 2), (2, 0), (3, 4)]
    _check(6, edges, tree_decomposition_width2(6, iter(edges)))
    assert tree_decomposition_width2(4, itertools.combinations(range(4), 2)) is None
    assert tree_decomposition_width2(0, []) == ([], [])
    with pytest.raises(ValueError):
        tree_decomposition_width2(-1, [])
    with pytest.raises(IndexError):
        tree_decomposition_width2(2, [(0, 2)])


def test_width2_long_cycle_and_parallel_paths():
    n = 20000
    edges = [(v, (v + 1) % n) for v in range(n)]
    _check(n, edges, tree_decomposition_width2(n, edges))
    edges = [(0, v) for v in range(2, n)] + [(v, 1) for v in range(2, n)]
    _check(n, edges, tree_decomposition_width2(n, edges))
