import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph_flow.MaxFlow import (
    MaxFlowGraph,
    feasible_circulation,
    max_flow_with_bounds,
)


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


def test_flow_with_bounds_and_circulation():
    circulation = [(0, 1, 1, 3), (1, 2, 1, 2), (2, 0, 1, 4)]
    flows = feasible_circulation(3, circulation)
    assert flows is not None
    balance = [0, 0, 0]
    for flow, (first, second, lower, upper) in zip(flows, circulation):
        assert lower <= flow <= upper
        balance[first] -= flow
        balance[second] += flow
    assert balance == [0, 0, 0]

    edges = [
        (0, 1, 1, 4),
        (0, 2, 0, 3),
        (1, 2, 0, 2),
        (1, 3, 1, 3),
        (2, 3, 1, 5),
    ]
    value, flows = max_flow_with_bounds(4, edges, 0, 3)
    brute = []
    for candidate in itertools.product(
        *[range(lower, upper + 1) for _, _, lower, upper in edges]
    ):
        balance = [0] * 4
        for flow, (first, second, _, _) in zip(candidate, edges):
            balance[first] -= flow
            balance[second] += flow
        if balance[1] == balance[2] == 0 and balance[0] == -balance[3]:
            brute.append(balance[3])
    assert value == max(brute)


def test_residual_graph_and_min_cut_edges():
    graph = MaxFlowGraph(4)
    graph.add_edge(0, 1, 2)
    graph.add_edge(0, 2, 1)
    graph.add_edge(1, 3, 2)
    graph.add_edge(2, 3, 1)
    assert graph.flow(0, 3) == 3
    assert graph.residual_graph()[0] == []
    cut = graph.min_cut_edges(0)
    assert [(source, target, capacity) for _, source, target, capacity, _ in cut] == [
        (0, 1, 2),
        (0, 2, 1),
    ]


def test_flow_value_and_path_decomposition():
    graph = MaxFlowGraph(6)
    edges = [
        (0, 1, 5),
        (0, 2, 4),
        (1, 2, 2),
        (1, 3, 3),
        (2, 4, 5),
        (3, 5, 4),
        (4, 3, 2),
        (4, 5, 4),
    ]
    for edge in edges:
        graph.add_edge(*edge)
    value = graph.flow(0, 5)
    paths = graph.flow_paths(0, 5)
    assert graph.flow_value(0) == value
    assert graph.flow_value(5) == -value
    assert sum(amount for amount, _, _ in paths) == value
    used = [0] * len(edges)
    for amount, vertices, edge_ids in paths:
        assert amount > 0
        assert vertices[0] == 0 and vertices[-1] == 5
        assert len(vertices) == len(edge_ids) + 1
        for index, edge_id in enumerate(edge_ids):
            assert edges[edge_id][:2] == (vertices[index], vertices[index + 1])
            used[edge_id] += amount
    for edge_id, flow in enumerate(used):
        assert flow <= graph.get_edge(edge_id)[3]


def test_flow_decomposition_ignores_circulation():
    graph = MaxFlowGraph(4)
    first = graph.add_edge(0, 1, 5)
    second = graph.add_edge(1, 3, 5)
    cycle_a = graph.add_edge(1, 2, 3)
    cycle_b = graph.add_edge(2, 1, 3)
    graph.change_edge(first, 5, 4)
    graph.change_edge(second, 5, 4)
    graph.change_edge(cycle_a, 3, 2)
    graph.change_edge(cycle_b, 3, 2)
    assert graph.flow_value(0) == 4
    assert graph.flow_paths(0, 3) == [(4, [0, 1, 3], [first, second])]


if __name__ == "__main__":
    random.seed(0)
    test_random_against_min_cut()
    test_limit_repeat_change_and_vertex()
    test_long_without_recursion()
