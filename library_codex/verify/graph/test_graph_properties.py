import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.GraphProperties import (  # noqa: E402
    ChordalGraphRecognizer,
    bipartite_edge_coloring,
)


def _graph(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph


def _brute_chordal(n, edges):
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    for size in range(4, n + 1):
        for vertices in itertools.combinations(range(n), size):
            chosen = set(vertices)
            if all(len(adjacency[v] & chosen) == 2 for v in vertices):
                seen = {vertices[0]}
                stack = [vertices[0]]
                while stack:
                    v = stack.pop()
                    for to in adjacency[v] & chosen:
                        if to not in seen:
                            seen.add(to)
                            stack.append(to)
                if len(seen) == size:
                    return False
    return True


def _is_peo(order, graph):
    position = [0] * len(graph)
    for i, v in enumerate(order):
        position[v] = i
    adjacency = [set(neighbors) for neighbors in graph]
    for v in order:
        later = [to for to in graph[v] if position[to] > position[v]]
        if any(b not in adjacency[a]
               for a, b in itertools.combinations(later, 2)):
            return False
    return True


def _is_induced_cycle(cycle, graph):
    if len(cycle) < 4 or len(cycle) != len(set(cycle)):
        return False
    adjacency = [set(neighbors) for neighbors in graph]
    chosen = set(cycle)
    return all(len(adjacency[v] & chosen) == 2 for v in cycle)


def test_chordal_recognizer_and_witness_against_bruteforce():
    rng = random.Random(22)
    for n in range(9):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(400):
            edges = [edge for edge in pairs if rng.randrange(2)]
            graph = _graph(n, edges)
            expected = _brute_chordal(n, edges)
            recognizer = ChordalGraphRecognizer(graph)
            assert recognizer.is_chordal() == expected
            assert sorted(recognizer.maximum_cardinality_search_order()) == list(range(n))
            if expected:
                assert _is_peo(recognizer.perfect_elimination_order(), graph)
                assert recognizer.induced_cycle() == []
            else:
                assert _is_induced_cycle(recognizer.induced_cycle(), graph)


def test_bipartite_edge_coloring_multigraph():
    rng = random.Random(23)
    for left_size in range(7):
        for right_size in range(7):
            if not left_size or not right_size:
                continue
            for _ in range(200):
                edges = [(rng.randrange(left_size), rng.randrange(right_size))
                         for _ in range(rng.randrange(30))]
                count, color = bipartite_edge_coloring(
                    left_size, right_size, edges
                )
                degree_left = [0] * left_size
                degree_right = [0] * right_size
                for u, v in edges:
                    degree_left[u] += 1
                    degree_right[v] += 1
                expected = max(max(degree_left, default=0),
                               max(degree_right, default=0))
                assert count == expected
                assert len(color) == len(edges)
                assert all(0 <= c < count for c in color) if edges else not color
                for vertex in range(left_size):
                    incident = [color[i] for i, (u, _) in enumerate(edges)
                                if u == vertex]
                    assert len(incident) == len(set(incident))
                for vertex in range(right_size):
                    incident = [color[i] for i, (_, v) in enumerate(edges)
                                if v == vertex]
                    assert len(incident) == len(set(incident))
