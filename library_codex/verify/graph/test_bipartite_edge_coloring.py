import random

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
