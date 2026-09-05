import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.graph_flow.PushRelabel import PushRelabel
from library_codex.graph_flow.MaxFlow import MaxFlowGraph


def brute_directed_min_cut(n, edges, source, sink):
    best = None
    for mask in range(1 << n):
        if not (mask >> source & 1) or mask >> sink & 1:
            continue
        value = sum(
            capacity
            for left, right, capacity in edges
            if mask >> left & 1 and not (mask >> right & 1)
        )
        if best is None or value < best:
            best = value
    return best


def validate_flow(graph, source, sink, value):
    balance = [0] * graph.n
    for u, v, capacity, flow in graph.edges():
        assert 0 <= flow <= capacity
        balance[u] -= flow
        balance[v] += flow
    assert -balance[source] == balance[sink] == value
    assert all(balance[v] == 0 for v in range(graph.n) if v not in (source, sink))


def test_push_relabel_random_against_bruteforce_and_dinic():
    rng = random.Random(801)
    for n in range(2, 9):
        for _ in range(500):
            source, sink = rng.sample(range(n), 2)
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(12))
                for _ in range(rng.randrange(20))
            ]
            fast = PushRelabel(n)
            dinic = MaxFlowGraph(n)
            for edge in edges:
                fast.add_edge(*edge)
                dinic.add_edge(*edge)
            want = brute_directed_min_cut(n, edges, source, sink)
            assert fast.flow(source, sink) == want
            validate_flow(fast, source, sink, want)
            assert dinic.flow(source, sink) == want
            side = fast.min_cut(source)
            assert side[source] and not side[sink]
            assert sum(
                capacity
                for left, right, capacity, _ in fast.edges()
                if side[left] and not side[right]
            ) == want


def test_push_relabel_api_repeat_change_and_long_path():
    graph = PushRelabel(4)
    ids = [
        graph.add_edge(0, 1, 5),
        graph.add_edge(0, 2, 7),
        graph.add_edge(1, 3, 6),
        graph.add_edge(2, 3, 4),
        graph.add_edge(1, 2, 3),
    ]
    assert graph.flow(0, 3) == 9
    validate_flow(graph, 0, 3, 9)
    assert graph.flow(0, 3) == 0
    assert graph.get_edge(ids[0])[:3] == (0, 1, 5)

    graph = PushRelabel(2)
    edge = graph.add_edge(0, 1, 10)
    graph.change_edge(edge, 7, 3)
    assert graph.get_edge(edge) == (0, 1, 7, 3)
    assert graph.flow(0, 1) == 4

    n = 100000
    graph = PushRelabel(n)
    for vertex in range(n - 1):
        graph.add_edge(vertex, vertex + 1, 1)
    assert graph.flow(0, n - 1) == 1


def test_push_relabel_flow_limit_matches_dinic():
    edges = [
        (0, 0, 100),
        (0, 1, 5),
        (0, 2, 7),
        (1, 3, 6),
        (2, 3, 4),
        (1, 2, 3),
    ]
    fast = PushRelabel(4)
    dinic = MaxFlowGraph(4)
    for edge in edges:
        fast.add_edge(*edge)
        dinic.add_edge(*edge)
    for limit in (0, 3, 4, 100):
        assert fast.flow(0, 3, limit) == dinic.flow(0, 3, limit)
        validate_flow(fast, 0, 3, dinic.flow_value(0))
        assert fast.n == 4 and len(fast.graph) == 4 and len(fast.position) == len(edges)
    assert fast.flow(0, 3) == dinic.flow(0, 3) == 0

    try:
        fast.flow(0, 3, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative flow limit must fail")

    rng = random.Random(804)
    for n in range(2, 9):
        for _ in range(200):
            source, sink = rng.sample(range(n), 2)
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(10))
                for _ in range(rng.randrange(20))
            ]
            fast = PushRelabel(n)
            dinic = MaxFlowGraph(n)
            for edge in edges:
                fast.add_edge(*edge)
                dinic.add_edge(*edge)
            applied_limits = []
            for _ in range(4):
                limit = rng.randrange(8)
                applied_limits.append(limit)
                fast_value = fast.flow(source, sink, limit)
                dinic_value = dinic.flow(source, sink, limit)
                assert fast_value == dinic_value, repr(
                    (n, source, sink, edges, applied_limits, fast_value, dinic_value)
                )
                validate_flow(fast, source, sink, dinic.flow_value(source))
            assert fast.flow(source, sink) == dinic.flow(source, sink)
            validate_flow(fast, source, sink, dinic.flow_value(source))


def test_large_excess_returns_to_source_and_repeat_after_add():
    graph = PushRelabel(8)
    edges = [(0, 1, 10**80), (1, 2, 10**80), (2, 3, 10**80),
             (3, 1, 10**80), (0, 4, 10**90), (4, 5, 10**90), (5, 7, 7)]
    for edge in edges:
        graph.add_edge(*edge)
    assert graph.flow(0, 7) == 7
    validate_flow(graph, 0, 7, 7)
    graph.add_edge(3, 7, 11)
    assert graph.flow(0, 7, 3) == 3
    validate_flow(graph, 0, 7, 10)
    assert graph.flow(0, 7) == 8
    validate_flow(graph, 0, 7, 18)
    assert graph.flow(0, 7) == 0
    graph.add_vertex()
    assert graph.n == 9
    assert graph.get_edge(0)[:3] == edges[0]


def test_medium_random_feasible_flows():
    rng = random.Random(905)
    for n in (20, 60, 180):
        for _ in range(30):
            fast, dinic = PushRelabel(n), MaxFlowGraph(n)
            for _ in range(n * 12):
                edge = rng.randrange(n), rng.randrange(n), rng.randrange(10**12)
                fast.add_edge(*edge)
                dinic.add_edge(*edge)
            source, sink = rng.sample(range(n), 2)
            value = dinic.flow(source, sink)
            assert fast.flow(source, sink) == value
            validate_flow(fast, source, sink, value)
            side = fast.min_cut(source)
            assert sum(c for u, v, c, _ in fast.edges() if side[u] and not side[v]) == value


def test_disconnected_empty_and_invalid_inputs():
    graph = PushRelabel(3)
    assert graph.flow(0, 2) == 0
    assert graph.min_cut(0) == [True, False, False]
    for capacity in (-1,):
        with pytest.raises(ValueError):
            graph.add_edge(0, 1, capacity)
    for capacity in (float("inf"), float("nan"), 1.5):
        with pytest.raises(TypeError):
            graph.add_edge(0, 1, capacity)
        with pytest.raises(TypeError):
            graph.flow(0, 2, capacity)
    with pytest.raises(ValueError):
        graph.flow(0, 0)
    with pytest.raises(IndexError):
        graph.add_edge(0, 3, 1)
    assert graph.edges() == []
