import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.GraphMatching import (  # noqa: E402
    DynamicBipartiteGraph,
    GeneralMatching,
    TwoSAT,
    dag_minimum_path_cover,
)


def _brute_matching(n, edges):
    best = 0
    for mask in range(1 << len(edges)):
        used = 0
        count = 0
        valid = True
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                bits = (1 << u) | (1 << v)
                if used & bits:
                    valid = False
                    break
                used |= bits
                count += 1
        if valid and count > best:
            best = count
    return best


def test_general_matching_against_edge_subsets():
    rng = random.Random(30)
    for n in range(10):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(400):
            rng.shuffle(possible)
            edges = possible[:rng.randrange(min(12, len(possible)) + 1)]
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)
            solver = GeneralMatching(graph)
            assert solver.matching_size == _brute_matching(n, edges)
            assert len(solver.pairs()) == solver.matching_size
            for u, v in solver.pairs():
                assert u in graph[v] and solver.mate[u] == v and solver.mate[v] == u


def test_two_sat_against_all_assignments():
    rng = random.Random(31)
    for n in range(9):
        for _ in range(500):
            clauses = [
                (rng.randrange(n), bool(rng.randrange(2)),
                 rng.randrange(n), bool(rng.randrange(2)))
                for _ in range(rng.randrange(20))
            ] if n else []
            expected = []
            for mask in range(1 << n):
                values = [bool(mask >> v & 1) for v in range(n)]
                if all(values[a] == av or values[b] == bv
                       for a, av, b, bv in clauses):
                    expected.append(values)
            solver = TwoSAT(n)
            for clause in clauses:
                solver.add_clause(*clause)
            answer = solver.solve()
            assert (answer is not None) == bool(expected)
            if answer is not None:
                assert all(answer[a] == av or answer[b] == bv
                           for a, av, b, bv in clauses)


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
