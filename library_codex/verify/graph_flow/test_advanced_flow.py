import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.graph_flow.AdvancedFlow import (
    gomory_hu_tree,
    stoer_wagner_min_cut,
)
from library_codex.graph_flow.MaxFlow import MaxFlowGraph




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
