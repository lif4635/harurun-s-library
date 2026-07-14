import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.MaxFlow import MaxFlowGraph


def brute_min_cut(n, edges, source, sink):
    best = None
    for mask in range(1 << n):
        if not (mask >> source & 1) or mask >> sink & 1:
            continue
        cost = sum(c for u, v, c in edges if mask >> u & 1 and not (mask >> v & 1))
        if best is None or cost < best:
            best = cost
    return best


def validate(graph, n, source, sink, expected):
    balance = [0] * n
    for u, v, cap, flow in graph.edges():
        assert 0 <= flow <= cap
        balance[u] -= flow
        balance[v] += flow
    assert -balance[source] == balance[sink] == expected
    assert all(balance[v] == 0 for v in range(n) if v not in (source, sink))
    cut = graph.min_cut(source)
    assert cut[source] and not cut[sink]
    assert sum(
        cap for u, v, cap, _ in graph.edges() if cut[u] and not cut[v]
    ) == expected


def test_random_against_min_cut():
    for n in range(2, 9):
        for _ in range(2000):
            source = random.randrange(n)
            sink = random.randrange(n - 1)
            if sink >= source:
                sink += 1
            edges = [
                (random.randrange(n), random.randrange(n), random.randrange(8))
                for _ in range(random.randrange(13))
            ]
            graph = MaxFlowGraph(n)
            for edge in edges:
                graph.add_edge(*edge)
            want = brute_min_cut(n, edges, source, sink)
            assert graph.flow(source, sink) == want
            validate(graph, n, source, sink, want)


def test_limit_repeat_change_and_vertex():
    edges = [(0, 1, 5), (0, 2, 7), (1, 3, 6), (2, 3, 4), (1, 2, 3)]
    graph = MaxFlowGraph(4)
    ids = [graph.add_edge(*edge) for edge in edges]
    assert graph.flow(0, 3, 3) == 3
    assert graph.flow(0, 3, 4) == 4
    assert graph.flow(0, 3) == 2
    assert graph.flow(0, 3) == 0
    assert graph.get_edge(ids[0])[:3] == edges[0]

    graph = MaxFlowGraph(1)
    assert graph.add_vertex() == 1
    edge = graph.add_edge(0, 1, 10)
    graph.change_edge(edge, 7, 3)
    assert graph.get_edge(edge) == (0, 1, 7, 3)
    assert graph.flow(0, 1) == 4


def test_long_without_recursion():
    n = 200000
    graph = MaxFlowGraph(n)
    for i in range(n - 1):
        graph.add_edge(i, i + 1, 1)
    assert graph.flow(0, n - 1) == 1


if __name__ == "__main__":
    random.seed(0)
    test_random_against_min_cut()
    test_limit_repeat_change_and_vertex()
    test_long_without_recursion()
