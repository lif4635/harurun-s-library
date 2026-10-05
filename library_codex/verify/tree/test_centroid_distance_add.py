import random

import pytest

from library_codex.tree.CentroidDistanceAdd import CentroidDistanceAdd


def test_random_updates_against_bfs():
    rng = random.Random(428879)
    for n in (1, 2, 3, 10, 40, 100):
        graph = [[] for _ in range(n)]
        for vertex in range(1, n):
            parent = rng.randrange(vertex)
            graph[parent].append(vertex)
            graph[vertex].append(parent)
        distance = []
        for start in range(n):
            row = [-1] * n
            row[start] = 0
            queue = [start]
            for vertex in queue:
                for other in graph[vertex]:
                    if row[other] < 0:
                        row[other] = row[vertex] + 1
                        queue.append(other)
            distance.append(row)
        values = [rng.randrange(-100, 101) for _ in range(n)]
        solver = CentroidDistanceAdd(graph, values)
        for step in range(500):
            vertex = rng.randrange(n)
            lower = rng.randrange(-2, n + 2)
            upper = None if step % 17 == 0 else rng.randrange(-2, n + 2)
            delta = rng.randrange(-10**20, 10**20)
            solver.add(vertex, lower, upper, delta)
            for other in range(n):
                if lower <= distance[vertex][other] and (upper is None or distance[vertex][other] < upper):
                    values[other] += delta
            assert solver.get(vertex) == values[vertex]
            if step % 43 == 0:
                assert solver.tolist() == values
                assert str(solver) == str(values)
                assert repr(solver) == "CentroidDistanceAdd(%r)" % values
                copy = solver.tolist()
                copy[0] += 1
                assert solver.get(0) == values[0]


def test_default_values_and_invalid_length():
    solver = CentroidDistanceAdd([[1], [0]])
    assert solver.tolist() == [0, 0]
    solver.add(0, 0, None, 7)
    assert solver.tolist() == [7, 7]
    with pytest.raises(ValueError):
        CentroidDistanceAdd([[1], [0]], [0])


def test_fractional_and_infinite_distance_bounds():
    from decimal import Decimal
    from fractions import Fraction

    graph = [[1], [0, 2], [1, 3], [2]]
    values = [2, 3, 5, 7]
    solver = CentroidDistanceAdd(graph, values)
    bounds = [-float("inf"), -0.5, 0, 0.5, Fraction(3, 2), Decimal("2.1"), 3, 4.5, float("inf")]
    for vertex in range(4):
        for lower in bounds:
            for upper in bounds:
                solver.add(vertex, lower, upper, 3)
                for other in range(4):
                    if lower <= abs(other - vertex) < upper:
                        values[other] += 3
                assert solver.tolist() == values
