import itertools
import random

import pytest

from library_codex.graph.GraphFromEdges import graph_from_edges
from library_codex.graph_enumeration.ChromaticNumber import chromatic_number


def _brute_chromatic(graph):
    n = len(graph)
    if n == 0:
        return 0
    color = [-1] * n
    for k in range(1, n + 1):
        stack = [(0, 0)]
        while stack:
            v, next_color = stack.pop()
            if v == n:
                return k
            if next_color == k:
                color[v] = -1
                continue
            stack.append((v, next_color + 1))
            if all(color[u] != next_color for u in graph[v] if u < v):
                color[v] = next_color
                stack.append((v + 1, 0))
    return n


def test_chromatic_number_against_bruteforce():
    rng = random.Random(0)
    for n in range(9):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            edges = [edge for edge in pairs if rng.randrange(2)]
            graph = graph_from_edges(n, edges)
            expected = _brute_chromatic(graph)
            assert chromatic_number(graph) == expected
            assert chromatic_number(graph, exact=True) == expected
