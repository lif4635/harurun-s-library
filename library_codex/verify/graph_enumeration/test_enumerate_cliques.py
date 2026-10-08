import itertools
import random

import pytest

from library_codex.graph.GraphFromEdges import graph_from_edges
from library_codex.graph_enumeration.EnumerateCliques import enumerate_cliques


def test_clique_enumeration_against_all_subsets():
    rng = random.Random(4)
    for n in range(10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(60):
            edges = [edge for edge in pairs if rng.randrange(2)]
            graph = graph_from_edges(n, edges)
            edge_set = set(edges)
            expected = set()
            for mask in range(1, 1 << n):
                vertices = tuple(v for v in range(n) if mask >> v & 1)
                if all((u, v) in edge_set
                       for u, v in itertools.combinations(vertices, 2)):
                    expected.add(vertices)
            actual = {tuple(vertices) for vertices in enumerate_cliques(graph)}
            assert actual == expected
            called = []
            count = enumerate_cliques(graph, called.append, include_empty=True)
            assert count == len(called) == len(expected) + 1
            assert [] in called
