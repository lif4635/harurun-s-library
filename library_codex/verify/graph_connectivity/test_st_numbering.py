import itertools
import random

import pytest

from library_codex.graph.CSRGraph import CSRGraph
from library_codex.graph_connectivity.STNumbering import st_numbering


def _valid(graph, source, target, rank):
    n = len(graph)
    if sorted(rank) != list(range(n)) or rank[source] != 0 or rank[target] != n - 1:
        return False
    return all((v == source or any(rank[u] < rank[v] for u in graph[v]))
               and (v == target or any(rank[u] > rank[v] for u in graph[v]))
               for v in range(n))


def _possible(graph, source, target):
    n = len(graph)
    middle = [v for v in range(n) if v not in (source, target)]
    for permutation in itertools.permutations(middle):
        rank = [0] * n
        for i, v in enumerate((source,) + permutation + (target,)):
            rank[v] = i
        if _valid(graph, source, target, rank):
            return True
    return False


def test_st_numbering_against_permutations():
    rng = random.Random(605014)
    for n in range(2, 8):
        pairs = list(itertools.combinations(range(n), 2))
        masks = range(1 << len(pairs)) if n <= 4 else [rng.getrandbits(len(pairs)) for _ in range(180)]
        for mask in masks:
            graph = [[] for _ in range(n)]
            edges = [e for i, e in enumerate(pairs) if mask >> i & 1]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)
            source, target = rng.sample(range(n), 2)
            before = [row[:] for row in graph]
            rank = st_numbering(graph, source, target)
            assert (rank is not None) == _possible(graph, source, target)
            assert graph == before
            csr_rank = st_numbering(CSRGraph(n, edges, directed=False), source, target)
            assert (csr_rank is None) == (rank is None)
            if rank is not None:
                assert _valid(graph, source, target, rank)
                assert _valid(graph, source, target, csr_rank)


def test_st_numbering_boundaries_and_long_path():
    assert st_numbering([[]], 0, 0) == [0]
    assert st_numbering([[1, 1, 0], [0, 0]], 0, 1) == [0, 1]
    assert st_numbering([[1], [0], []], 0, 1) is None
    assert st_numbering([[1], [0]], 0, 0) is None
    with pytest.raises(IndexError):
        st_numbering([[]], 0, 1)
    with pytest.raises(ValueError):
        st_numbering(CSRGraph(2, [(0, 1)]), 0, 1)
    n = 30000
    graph = [[] for _ in range(n)]
    for v in range(n - 1):
        graph[v].append(v + 1)
        graph[v + 1].append(v)
    assert st_numbering(graph, 0, n - 1) == list(range(n))
    assert st_numbering(graph, 0, n - 2) is None
    graph[0].append(n - 1)
    graph[n - 1].append(0)
    assert _valid(graph, 0, n // 2, st_numbering(graph, 0, n // 2))
