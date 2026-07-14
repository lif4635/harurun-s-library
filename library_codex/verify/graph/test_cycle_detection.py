import random
import sys
from collections import deque
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.CycleDetection import cycle_detection, find_cycle


def brute_directed(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    que = deque(v for v in range(n) if indeg[v] == 0)
    count = 0
    while que:
        u = que.popleft()
        count += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                que.append(v)
    return count != n


def brute_undirected(n, edges):
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for u, v in edges:
        u = root(u)
        v = root(v)
        if u == v:
            return True
        parent[v] = u
    return False


def validate(edges, directed, vertices, cycle_edges):
    assert vertices and len(vertices) == len(cycle_edges)
    assert len(set(cycle_edges)) == len(cycle_edges)
    for i, eid in enumerate(cycle_edges):
        u = vertices[i]
        v = vertices[(i + 1) % len(vertices)]
        a, b = edges[eid]
        if directed:
            assert (u, v) == (a, b)
        else:
            assert (u, v) == (a, b) or (u, v) == (b, a)


def test_random():
    for directed in (False, True):
        for n in range(1, 100):
            for _ in range(100):
                edges = [(random.randrange(n), random.randrange(n)) for _ in range(n * 3)]
                vertices, cycle_edges = find_cycle(n, edges, directed)
                want = brute_directed(n, edges) if directed else brute_undirected(n, edges)
                assert bool(cycle_edges) == want
                assert cycle_detection(n, edges, directed) == cycle_edges
                if cycle_edges:
                    validate(edges, directed, vertices, cycle_edges)


def test_parallel_and_self_loop():
    validate([(0, 0)], False, *find_cycle(1, [(0, 0)], False))
    validate([(0, 1), (0, 1)], False, *find_cycle(2, [(0, 1), (0, 1)], False))
    assert find_cycle(2, [(0, 1), (0, 1)], True) == ([], [])


def test_large_without_recursion():
    n = 200000
    edges = [(i, i + 1) for i in range(n - 1)] + [(n - 1, 0)]
    vertices, cycle_edges = find_cycle(n, edges, True)
    assert len(vertices) == n
    assert cycle_edges == list(range(n))


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_parallel_and_self_loop()
    test_large_without_recursion()
