from collections import Counter
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.OfflineDynamicConnectivity import (
    OfflineDynamicConnectivity,
)


def brute_state(n, edges, values):
    graph = [[] for _ in range(n)]
    for (u, v), count in edges.items():
        if count:
            graph[u].append(v)
            graph[v].append(u)
    component = [-1] * n
    groups = []
    for root in range(n):
        if component[root] != -1:
            continue
        cid = len(groups)
        component[root] = cid
        group = []
        stack = [root]
        while stack:
            v = stack.pop()
            group.append(v)
            for to in graph[v]:
                if component[to] == -1:
                    component[to] = cid
                    stack.append(to)
        groups.append(group)
    sizes = [0] * len(groups)
    sums = [0] * len(groups)
    for v in range(n):
        sizes[component[v]] += 1
        sums[component[v]] += values[v]
    return component, sizes, sums


def test_random_against_brute():
    rng = random.Random(1)
    for _ in range(1000):
        n = rng.randrange(1, 9)
        q = rng.randrange(1, 40)
        initial = [rng.randrange(-20, 21) for _ in range(n)]
        values = initial.copy()
        edges = Counter()
        dc = OfflineDynamicConnectivity(n, q, initial)
        expected = []
        for time in range(q):
            action = rng.randrange(4)
            active_edges = [edge for edge, count in edges.items() if count]
            if action <= 1 or not active_edges:
                u = rng.randrange(n)
                v = rng.randrange(n)
                edge = (u, v) if u <= v else (v, u)
                edges[edge] += 1
                dc.add_edge(time, u, v)
            elif action == 2:
                edge = rng.choice(active_edges)
                edges[edge] -= 1
                dc.remove_edge(time, *edge)
            else:
                v = rng.randrange(n)
                delta = rng.randrange(-20, 21)
                values[v] += delta
                dc.add_vertex_value(time, v, delta)

            component, sizes, sums = brute_state(n, edges, values)
            u = rng.randrange(n)
            v = rng.randrange(n)
            assert dc.query_same(time, u, v) == len(expected)
            expected.append(component[u] == component[v])
            dc.query_size(time, u)
            expected.append(sizes[component[u]])
            dc.query_components(time)
            expected.append(len(sizes))
            dc.query_component_sum(time, v)
            expected.append(sums[component[v]])
        assert dc.solve() == expected


def test_parallel_edges_and_callbacks():
    dc = OfflineDynamicConnectivity(4, 8)
    dc.add_edge(0, 0, 1)
    dc.add_edge(1, 1, 0)
    dc.add_edge(2, 1, 2)
    dc.remove_edge(3, 0, 1)
    dc.query_same(4, 0, 2)
    dc.remove_edge(5, 0, 1)
    dc.query_same(6, 0, 2)
    dc.query_components(7)
    assert dc.solve() == [True, False, 3]

    forest = []
    seen = []

    def add(u, v):
        forest.append((u, v))

    def remove(u, v):
        forest.remove((u, v))

    def query(time, uf):
        seen.append(time)
        assert len(forest) == dc.n - uf.component_count

    dc.run(query, add, remove)
    assert seen == list(range(8))
    assert not forest
    assert dc.uf.component_count == 4


def test_invalid_remove_and_empty_timeline():
    dc = OfflineDynamicConnectivity(2, 1)
    dc.remove_edge(0, 0, 1)
    try:
        dc.build()
    except ValueError:
        pass
    else:
        assert False

    dc = OfflineDynamicConnectivity(0, 0)
    assert dc.solve() == []


def test_large_without_recursion():
    n = 50000
    q = n * 2
    dc = OfflineDynamicConnectivity(n, q)
    for time in range(n):
        dc.add_edge(time, time, (time + 1) % n)
    for time in range(n):
        dc.remove_edge(n + time, time, (time + 1) % n)
    dc.query_components(q - 1)
    assert dc.solve() == [n]


if __name__ == "__main__":
    test_random_against_brute()
    test_parallel_edges_and_callbacks()
    test_invalid_remove_and_empty_timeline()
    test_large_without_recursion()
