import random
import pytest

from library_codex.graph_matching.BipartiteEdgeColoring import (
    bipartite_edge_coloring,
)


def test_bipartite_edge_coloring_random_multigraphs():
    random.seed(20260826)
    for left_size in range(7):
        for right_size in range(7):
            for _ in range(120):
                if not left_size or not right_size:
                    edges = []
                else:
                    edges = [(random.randrange(left_size), random.randrange(right_size))
                             for _ in range(random.randrange(25))]
                colors = bipartite_edge_coloring(left_size, right_size, edges)
                degree = [0] * (left_size + right_size)
                seen = [set() for _ in degree]
                for edge_id, ((left, right), color) in enumerate(zip(edges, colors)):
                    assert color not in seen[left]
                    assert color not in seen[left_size + right]
                    seen[left].add(color)
                    seen[left_size + right].add(color)
                    degree[left] += 1
                    degree[left_size + right] += 1
                delta = max(degree, default=0)
                assert (max(colors) + 1 if colors else 0) == delta


def validate(left_size, right_size, edges):
    original = edges[:]
    colors = bipartite_edge_coloring(left_size, right_size, edges)
    assert edges == original
    assert len(colors) == len(edges)
    used = [set() for _ in range(left_size + right_size)]
    degree = [0] * len(used)
    for (u, v), color in zip(edges, colors):
        assert color >= 0
        assert color not in used[u]
        assert color not in used[left_size + v]
        used[u].add(color)
        used[left_size + v].add(color)
        degree[u] += 1
        degree[left_size + v] += 1
    assert max(colors, default=-1) + 1 == max(degree, default=0)


def test_regular_odd_degrees_and_disconnected_cycles():
    rng = random.Random(225)
    for size in (2, 3, 10, 31, 100):
        for degree in (2, 3, 5, 6, 7, 9, 15, 16, 17, 31):
            edges = []
            for _ in range(degree):
                permutation = list(range(size))
                rng.shuffle(permutation)
                edges.extend(enumerate(permutation))
            rng.shuffle(edges)
            validate(size, size, edges)
    validate(100, 100, [(i, i) for i in range(100)] * 2)


def test_high_degree_and_many_isolated_vertices():
    validate(100000, 100000, [(99999, i) for i in range(10000)])
    validate(100000, 100000, [(99999, 99999)] * 10000)
    validate(50000, 50000, [(0, i) for i in range(2000)] + [(i, 49999) for i in range(2000)])


def test_invalid_input_and_empty():
    assert bipartite_edge_coloring(0, 0, []) == []
    for args in [(-1, 0, []), (0, -1, [])]:
        with pytest.raises(ValueError):
            bipartite_edge_coloring(*args)
    for edges in [[(-1, 0)], [(0, -1)], [(2, 0)], [(0, 2)]]:
        with pytest.raises(IndexError):
            bipartite_edge_coloring(2, 2, edges)
