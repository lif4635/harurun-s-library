import itertools
import random

import pytest

from library_codex.graph.GraphFromEdges import graph_from_edges
from library_codex.graph_enumeration.CountC4PerEdge import count_c4_per_edge


def _brute_c4(n, edges, weight):
    edge_id = {edge: i for i, edge in enumerate(edges)}
    answer = [0] * len(edges)
    for vertices in itertools.combinations(range(n), 4):
        first = vertices[0]
        for tail in itertools.permutations(vertices[1:]):
            cycle = (first,) + tail
            if cycle[1] > cycle[3]:
                continue
            pairs = [tuple(sorted((cycle[i], cycle[(i + 1) & 3])))
                     for i in range(4)]
            if all(pair in edge_id for pair in pairs):
                ids = [edge_id[pair] for pair in pairs]
                for i, edge in enumerate(ids):
                    product = 1
                    for j in range(4):
                        if i != j:
                            product *= weight[ids[j]]
                    answer[edge] += product
    return answer


def test_count_c4_per_edge_weighted_against_bruteforce():
    rng = random.Random(5)
    for n in range(1, 10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            edges = [edge for edge in pairs if rng.randrange(3) == 0]
            weight = [rng.randrange(-3, 5) for _ in edges]
            assert count_c4_per_edge(n, edges, weight) == _brute_c4(
                n, edges, weight
            )
            assert count_c4_per_edge(n, edges) == _brute_c4(
                n, edges, [1] * len(edges)
            )


def _brute_multigraph(edges, weights):
    answer = [0] * len(edges)
    for ids in itertools.combinations(range(len(edges)), 4):
        degrees = {}
        pairs = set()
        for i in ids:
            u, v = edges[i]
            degrees[u] = degrees.get(u, 0) + 1
            degrees[v] = degrees.get(v, 0) + 1
            pairs.add(tuple(sorted((u, v))))
        if len(degrees) != 4 or len(pairs) != 4 or any(d != 2 for d in degrees.values()):
            continue
        for i in ids:
            value = 1
            for j in ids:
                if i != j:
                    value *= weights[j]
            answer[i] += value
    return answer


def test_parallel_edges_signed_weights_and_zero_sums():
    rng = random.Random(418309)
    for n in range(2, 9):
        for _ in range(60):
            edges = []
            for _ in range(rng.randrange(13)):
                u, v = rng.sample(range(n), 2)
                edges.append((u, v))
            weights = [rng.randrange(-3, 4) for _ in edges]
            original = edges[:], weights[:]
            assert count_c4_per_edge(n, edges, weights) == _brute_multigraph(edges, weights)
            assert count_c4_per_edge(n, edges) == _brute_multigraph(edges, [1] * len(edges))
            assert (edges, weights) == original
    edges = [(0, 1), (1, 0), (1, 2), (2, 3), (3, 0)]
    assert count_c4_per_edge(4, edges, [2, -2, 1, 1, 1]) == [1, 1, 0, 0, 0]
    assert count_c4_per_edge(4, edges) == [1, 1, 2, 2, 2]


def test_c4_boundaries_and_large_parallel_bundles():
    assert count_c4_per_edge(0, []) == []
    assert count_c4_per_edge(2, [(0, 1)] * 10000) == [0] * 10000
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)] * 1000
    assert count_c4_per_edge(4, edges) == [1000**3] * 4000
    with pytest.raises(ValueError):
        count_c4_per_edge(1, [(0, 0)])
    with pytest.raises(IndexError):
        count_c4_per_edge(2, [(0, 2)])
    with pytest.raises(ValueError):
        count_c4_per_edge(2, [(0, 1)], [])
