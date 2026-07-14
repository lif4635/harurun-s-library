import heapq
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.MinimumSpanningTree import (
    kruskal,
    minimum_spanning_forest,
    minimum_spanning_tree,
)


def prim_forest(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    used = [False] * n
    cost = 0
    components = 0
    for start in range(n):
        if used[start]:
            continue
        components += 1
        que = [(0, start)]
        while que:
            w, u = heapq.heappop(que)
            if used[u]:
                continue
            used[u] = True
            cost += w
            for edge in adj[u]:
                if not used[edge[1]]:
                    heapq.heappush(que, edge)
    return cost, components


def validate(n, edges, selected, components):
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for eid in selected:
        u, v, _ = edges[eid]
        u = root(u)
        v = root(v)
        assert u != v
        parent[v] = u
    assert len(selected) == n - components


def test_random():
    for n in range(0, 100):
        for _ in range(100):
            m = random.randrange(0, n * 5 + 1)
            edges = []
            for _ in range(m):
                u = random.randrange(n) if n else 0
                v = random.randrange(n) if n else 0
                edges.append((u, v, random.randrange(-10**9, 10**9)))
            cost, selected, components = minimum_spanning_forest(n, edges)
            want, want_components = prim_forest(n, edges)
            assert cost == want
            assert components == want_components
            assert kruskal(n, edges) == want
            validate(n, edges, selected, components)
            tree = minimum_spanning_tree(n, edges)
            if components <= 1:
                assert tree == (cost, selected)
            else:
                assert tree is None


def test_large_without_recursion():
    n = 200000
    edges = [(i, i + 1, (i * 97) & 1023) for i in range(n - 1)]
    edges += [(i, (i * 1000003 + 97) % n, 10**9 + i) for i in range(n)]
    cost, selected = minimum_spanning_tree(n, edges)
    assert len(selected) == n - 1
    assert cost == sum((i * 97) & 1023 for i in range(n - 1))


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_large_without_recursion()
