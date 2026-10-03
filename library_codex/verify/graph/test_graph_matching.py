import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph_matching.DAGMinimumPathCover import dag_minimum_path_cover  # noqa: E402
from graph_connectivity.DynamicBipartiteGraph import DynamicBipartiteGraph  # noqa: E402


def _bipartite_components(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    color = [-1] * n
    total = 0
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        count = [1, 0]
        queue = [start]
        for v in queue:
            for to in graph[v]:
                if color[to] == -1:
                    color[to] = color[v] ^ 1
                    count[color[to]] += 1
                    queue.append(to)
                elif color[to] == color[v]:
                    return False, -1
        total += max(count)
    return True, total


def test_dynamic_bipartite_after_every_edge():
    rng = random.Random(32)
    for n in range(1, 50):
        for _ in range(100):
            solver = DynamicBipartiteGraph(n)
            edges = []
            for _ in range(100):
                u = rng.randrange(n)
                v = rng.randrange(n)
                can = solver.can_add_edge(u, v)
                expected_can, _ = _bipartite_components(n, edges + [(u, v)])
                assert can == expected_can
                solver.add_edge(u, v)
                edges.append((u, v))
                expected, total = _bipartite_components(n, edges)
                assert solver.is_bipartite() == expected
                assert solver.maximum_side_sum == total


def test_dag_minimum_path_cover_against_matching_subsets():
    rng = random.Random(33)
    for n in range(10):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(300):
            edges = [edge for edge in possible if rng.randrange(4) == 0]
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
            paths = dag_minimum_path_cover(graph)
            assert sorted(v for path in paths for v in path) == list(range(n))
            edge_set = set(edges)
            assert all((path[i], path[i + 1]) in edge_set
                       for path in paths for i in range(len(path) - 1))
            # A matching edge set has distinct sources and targets.
            best = 0
            for mask in range(1 << len(edges)):
                selected = [edges[i] for i in range(len(edges)) if mask >> i & 1]
                if (len({u for u, _ in selected}) == len(selected)
                        and len({v for _, v in selected}) == len(selected)):
                    best = max(best, len(selected))
            assert len(paths) == n - best
