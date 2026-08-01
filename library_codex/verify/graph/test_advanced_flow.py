import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.graph.AdvancedFlow import (
    PushRelabelMaxFlow,
    gomory_hu_tree,
    stoer_wagner_min_cut,
)
from library_codex.graph.MaxFlow import MaxFlowGraph


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


def brute_undirected_min_cut(n, edges, source=None, sink=None):
    best = None
    for mask in range(1, 1 << n):
        if source is None:
            if mask == (1 << n) - 1:
                continue
        elif not (mask >> source & 1) or mask >> sink & 1:
            continue
        value = sum(
            capacity
            for left, right, capacity in edges
            if ((mask >> left) ^ (mask >> right)) & 1
        )
        if best is None or value < best:
            best = value
    return best


def tree_pair_minimum(n, tree, source, sink):
    graph = [[] for _ in range(n)]
    for left, right, value in tree:
        graph[left].append((right, value))
        graph[right].append((left, value))
    stack = [(source, -1, None)]
    while stack:
        vertex, parent, value = stack.pop()
        if vertex == sink:
            return value
        for other, weight in graph[vertex]:
            if other != parent:
                next_value = weight if value is None else min(value, weight)
                stack.append((other, vertex, next_value))
    raise AssertionError("cut tree is disconnected")


def test_push_relabel_random_against_bruteforce_and_dinic():
    rng = random.Random(801)
    for n in range(2, 9):
        for _ in range(500):
            source, sink = rng.sample(range(n), 2)
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(12))
                for _ in range(rng.randrange(20))
            ]
            fast = PushRelabelMaxFlow(n)
            dinic = MaxFlowGraph(n)
            for edge in edges:
                fast.add_edge(*edge)
                dinic.add_edge(*edge)
            want = brute_directed_min_cut(n, edges, source, sink)
            assert fast.flow(source, sink) == want
            assert dinic.flow(source, sink) == want
            side = fast.min_cut(source)
            assert side[source] and not side[sink]
            assert sum(
                capacity
                for left, right, capacity, _ in fast.edges()
                if side[left] and not side[right]
            ) == want


def test_push_relabel_api_repeat_change_and_long_path():
    graph = PushRelabelMaxFlow(4)
    ids = [
        graph.add_edge(0, 1, 5),
        graph.add_edge(0, 2, 7),
        graph.add_edge(1, 3, 6),
        graph.add_edge(2, 3, 4),
        graph.add_edge(1, 2, 3),
    ]
    assert graph.flow(0, 3) == 9
    assert graph.flow(0, 3) == 0
    assert graph.get_edge(ids[0])[:3] == (0, 1, 5)

    graph = PushRelabelMaxFlow(2)
    edge = graph.add_edge(0, 1, 10)
    graph.change_edge(edge, 7, 3)
    assert graph.get_edge(edge) == (0, 1, 7, 3)
    assert graph.flow(0, 1) == 4

    n = 100000
    graph = PushRelabelMaxFlow(n)
    for vertex in range(n - 1):
        graph.add_edge(vertex, vertex + 1, 1)
    assert graph.flow(0, n - 1) == 1


def test_gomory_hu_random_pair_cuts():
    rng = random.Random(802)
    for n in range(2, 9):
        for _ in range(120):
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(8))
                for _ in range(rng.randrange(18))
            ]
            tree = gomory_hu_tree(n, edges)
            assert len(tree) == n - 1
            for source in range(n):
                for sink in range(source + 1, n):
                    want = brute_undirected_min_cut(n, edges, source, sink)
                    assert tree_pair_minimum(n, tree, source, sink) == want


def test_stoer_wagner_random_global_cut():
    rng = random.Random(803)
    assert stoer_wagner_min_cut(0, []) == (0, [])
    assert stoer_wagner_min_cut(1, []) == (0, [0])
    for n in range(2, 9):
        for _ in range(500):
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(8))
                for _ in range(rng.randrange(20))
            ]
            want = brute_undirected_min_cut(n, edges)
            value, side = stoer_wagner_min_cut(n, edges)
            assert value == want
            selected = set(side)
            assert value == sum(
                capacity
                for left, right, capacity in edges
                if (left in selected) != (right in selected)
            )
