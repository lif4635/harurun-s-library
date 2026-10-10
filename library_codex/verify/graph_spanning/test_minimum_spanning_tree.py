import heapq
import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph_spanning.MinimumSpanningTree import (
    kruskal,
    manhattan_mst,
    second_spanning_tree,
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


def test_manhattan_mst_against_complete_graph_kruskal():
    rng = random.Random(130)
    for n in range(1, 80):
        for _ in range(100):
            points = [(rng.randrange(-100, 101), rng.randrange(-100, 101))
                      for _ in range(n)]
            complete = [
                (u, v, abs(points[u][0] - points[v][0])
                 + abs(points[u][1] - points[v][1]))
                for u in range(n) for v in range(u + 1, n)
            ]
            expected, _ = minimum_spanning_tree(n, complete)
            value, edges = manhattan_mst(points)
            assert value == expected
            assert len(edges) == n - 1
            assert value == sum(abs(points[u][0] - points[v][0])
                                + abs(points[u][1] - points[v][1])
                                for u, v in edges)


def _all_spanning_tree_costs(n, edges):
    result = []
    for chosen in itertools.combinations(range(len(edges)), n - 1):
        parent = list(range(n))
        def find(v):
            while parent[v] != v:
                v = parent[v]
            return v
        for edge_id in chosen:
            first, second, _ = edges[edge_id]
            first, second = find(first), find(second)
            if first != second:
                parent[second] = first
        if len({find(v) for v in range(n)}) == 1:
            result.append((sum(edges[i][2] for i in chosen), tuple(chosen)))
    return sorted(result)


def test_second_spanning_tree_random_against_enumeration():
    random.seed(20260824)
    for n in range(2, 8):
        for _ in range(120):
            edges = [(i, i + 1, random.randrange(1, 7)) for i in range(n - 1)]
            for i in range(n):
                for j in range(i + 2, n):
                    if random.randrange(2):
                        edges.append((i, j, random.randrange(1, 7)))
            all_trees = _all_spanning_tree_costs(n, edges)
            got = second_spanning_tree(n, edges)
            if len(all_trees) < 2:
                assert got is None
            else:
                assert got is not None
                mst_cost, second_cost, mst_edges, second_edges, added, removed = got
                assert mst_cost == all_trees[0][0]
                expected = min(cost for cost, chosen in all_trees
                               if set(chosen) != set(mst_edges))
                assert second_cost == expected
                assert set(second_edges) == set(mst_edges) - {removed} | {added}
            strict = second_spanning_tree(n, edges, strict=True)
            larger = [cost for cost, _ in all_trees if cost > all_trees[0][0]]
            assert (None if not larger else strict[1]) == (
                None if not larger else min(larger)
            )


def test_manhattan_boundaries_and_coordinate_ties():
    for points in ([], [(3, -7)], [(2, 2)] * 100, [(i, 0) for i in range(100)],
                   [(0, i) for i in range(100)], [(i, -i) for i in range(-50, 50)],
                   [(10**40, -10**40), (-10**40, 10**40), (0, 0)]):
        original = points[:]
        value, selected = manhattan_mst(points)
        n = len(points)
        complete = [(u, v, abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1]))
                    for u in range(n) for v in range(u)]
        assert value == minimum_spanning_tree(n, complete)[0]
        assert len(selected) == max(0, n - 1)
        assert points == original
