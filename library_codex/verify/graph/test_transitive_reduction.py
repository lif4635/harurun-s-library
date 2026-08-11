import random

import pytest

from library_codex.graph.TransitiveReduction import transitive_reduction


def _closure(graph):
    result = []
    for start in range(len(graph)):
        seen = 1 << start
        stack = [start]
        while stack:
            vertex = stack.pop()
            for edge in graph[vertex]:
                to = edge if isinstance(edge, int) else edge[0]
                if not seen >> to & 1:
                    seen |= 1 << to
                    stack.append(to)
        result.append(seen)
    return result


def test_random_dag_preserves_closure_and_is_minimal():
    random.seed(20260814)
    for n in range(1, 11):
        for _ in range(100):
            order = list(range(n))
            random.shuffle(order)
            graph = [[] for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if random.randrange(4) == 0:
                        graph[order[i]].append(order[j])
            reduced = transitive_reduction(graph)
            assert _closure(reduced) == _closure(graph)
            for vertex, row in enumerate(reduced):
                for index, to in enumerate(row):
                    removed = [values[:] for values in reduced]
                    removed[vertex].pop(index)
                    assert not (_closure(removed)[vertex] >> to & 1)


def test_tuple_edges_duplicates_and_cycle():
    graph = [[(1, 7), (1, 9), (2, 4)], [(2, 3)], []]
    assert transitive_reduction(graph) == [[1], [2], []]
    with pytest.raises(ValueError):
        transitive_reduction([[1], [0]])
    with pytest.raises(IndexError):
        transitive_reduction([[2], []])
