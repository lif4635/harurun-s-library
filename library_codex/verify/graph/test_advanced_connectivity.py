import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.AdvancedConnectivity import (  # noqa: E402
    ThreeEdgeConnectedComponents,
    incremental_scc_offline,
)
from graph.StronglyConnectedComponents import (  # noqa: E402
    StronglyConnectedComponents,
)


def _connected_after_removal(n, edges, source, target, removed):
    graph = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        if edge_id not in removed and u != v:
            graph[u].append(v)
            graph[v].append(u)
    seen = {source}
    stack = [source]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return target in seen


def _k_edge_connected(n, edges, source, target, k):
    if source == target:
        return True
    for size in range(k):
        for removed in itertools.combinations(range(len(edges)), size):
            if not _connected_after_removal(
                    n, edges, source, target, set(removed)):
                return False
    return True


def test_three_edge_components_against_all_small_edge_cuts():
    rng = random.Random(80)
    for n in range(10):
        possible = [(u, v) for u in range(n) for v in range(u, n)]
        for _ in range(120):
            edges = ([rng.choice(possible) for _ in range(rng.randrange(13))]
                     if possible else [])
            solver = ThreeEdgeConnectedComponents(n, edges)
            assert sorted(v for group in solver.groups for v in group) == list(range(n))
            assert sorted(v for group in solver.groups2 for v in group) == list(range(n))
            for u in range(n):
                for v in range(n):
                    assert ((solver.component2[u] == solver.component2[v])
                            == _k_edge_connected(n, edges, u, v, 2))
                    assert ((solver.component[u] == solver.component[v])
                            == _k_edge_connected(n, edges, u, v, 3))


class _DSU:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, v):
        while self.parent[v] != v:
            self.parent[v] = self.parent[self.parent[v]]
            v = self.parent[v]
        return v

    def unite(self, u, v):
        u = self.find(u)
        v = self.find(v)
        if u != v:
            self.parent[v] = u


def test_incremental_scc_union_edges_after_every_prefix():
    rng = random.Random(81)
    for n in range(1, 13):
        for _ in range(80):
            edges = [(rng.randrange(n), rng.randrange(n))
                     for _ in range(rng.randrange(22))]
            additions = incremental_scc_offline(n, edges)
            assert len(additions) == len(edges)
            dsu = _DSU(n)
            graph = [[] for _ in range(n)]
            used_edge_ids = set()
            for time, (u, v) in enumerate(edges):
                graph[u].append(v)
                for edge_id in additions[time]:
                    assert 0 <= edge_id <= time
                    assert edge_id not in used_edge_ids
                    used_edge_ids.add(edge_id)
                    a, b = edges[edge_id]
                    dsu.unite(a, b)
                component = StronglyConnectedComponents(graph).component
                for a in range(n):
                    for b in range(n):
                        assert ((dsu.find(a) == dsu.find(b))
                                == (component[a] == component[b]))
