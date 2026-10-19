from itertools import product
import random

import pytest

from library_codex.graph_enumeration.ChromaticPolynomial import chromatic_polynomial


def _evaluate(coefficients, value, mod):
    result = 0
    for coefficient in reversed(coefficients):
        result = (result * value + coefficient) % mod
    return result


def test_random_graphs_against_colorings():
    rng = random.Random(63027)
    for n in range(7):
        for _ in range(12):
            graph = [[] for _ in range(n)]
            edges = [(i, j) for i in range(n) for j in range(i) if rng.randrange(2)]
            for a, b in edges:
                graph[a].append(b)
                graph[b].append(a)
            saved = [row.copy() for row in graph]
            for mod in (998244353, 12):
                coefficients = chromatic_polynomial(graph, mod)
                assert len(coefficients) == n + 1
                for colors in range(4):
                    count = sum(all(assignment[a] != assignment[b] for a, b in edges)
                                for assignment in product(range(colors), repeat=n))
                    assert _evaluate(coefficients, colors, mod) == count % mod
            assert graph == saved


def test_loops_duplicates_disconnected_and_complete():
    assert chromatic_polynomial([]) == [1]
    assert chromatic_polynomial([[], [], []]) == [0, 0, 0, 1]
    assert chromatic_polynomial([[0], []]) == [0, 0, 0]
    assert chromatic_polynomial([[1, 1], [], [3], []], 100) == [0, 0, 1, 98, 1]
    assert chromatic_polynomial([[1, 2], [0, 2], [0, 1]], 100) == [0, 2, 97, 1]
    assert chromatic_polynomial([[1, 3], [2], [3], []], 100) == [0, 97, 6, 96, 1]
    for n in (10, 20):
        graph = [list(range(i)) + list(range(i + 1, n)) for i in range(n)]
        coefficients = chromatic_polynomial(graph)
        assert all(_evaluate(coefficients, k, 998244353) == 0 for k in range(n))


def test_invalid_inputs():
    for graph in ([[-1]], [[1]], [[], [2]]):
        with pytest.raises(ValueError):
            chromatic_polynomial(graph)
    with pytest.raises(ValueError):
        chromatic_polynomial([], 1)
