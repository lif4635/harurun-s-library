import itertools
import random

import pytest

from library_codex.graph.GraphFromEdges import graph_from_edges
from library_codex.graph_enumeration.MaximumIndependentSet import maximum_independent_set, maximum_independent_set_mask, maximum_weight_independent_set


def _is_independent(mask, graph):
    for v, neighbors in enumerate(graph):
        if mask >> v & 1:
            for u in neighbors:
                if u > v and mask >> u & 1:
                    return False
    return True


def test_maximum_independent_set_against_all_subsets():
    rng = random.Random(1)
    for n in range(11):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(100):
            graph = graph_from_edges(
                n, [edge for edge in pairs if rng.randrange(3) == 0]
            )
            expected = max(mask.bit_count() for mask in range(1 << n)
                           if _is_independent(mask, graph))
            size, mask = maximum_independent_set_mask(graph)
            vertices = maximum_independent_set(graph)
            assert size == expected == len(vertices) == mask.bit_count()
            assert _is_independent(mask, graph)


def test_maximum_weight_independent_set_against_all_subsets():
    rng = random.Random(2)
    for n in range(10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            graph = graph_from_edges(
                n, [edge for edge in pairs if rng.randrange(3) == 0]
            )
            weight = [rng.randrange(-5, 11) for _ in range(n)]
            expected = max(
                sum(weight[v] for v in range(n) if mask >> v & 1)
                for mask in range(1 << n) if _is_independent(mask, graph)
            )
            value, mask = maximum_weight_independent_set(graph, weight)
            assert value == expected
            assert value == sum(weight[v] for v in range(n) if mask >> v & 1)
            assert _is_independent(mask, graph)
