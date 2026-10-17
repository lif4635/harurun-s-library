from itertools import product, permutations
import random

import pytest

from library_codex.geometry.TrianglePointCounter import TrianglePointCounter


def _naive(vertices, points, a, b, c):
    triangle = [vertices[a], vertices[b], vertices[c]]
    total = 0
    for x, y in points:
        signs = []
        for i in range(3):
            ax, ay = triangle[i]
            bx, by = triangle[(i + 1) % 3]
            signs.append((bx - ax) * (y - ay) - (by - ay) * (x - ax))
        total += all(value > 0 for value in signs) or all(value < 0 for value in signs)
    return total


def test_random_against_cross_products():
    rng = random.Random(725841)
    for scale in (3, 10**9, 10**30):
        for _ in range(35):
            vertices = [(rng.randint(-scale, scale), rng.randint(-scale, scale)) for _ in range(8)]
            points = [(rng.randint(-scale, scale), rng.randint(-scale, scale)) for _ in range(15)] + vertices
            counter = TrianglePointCounter(vertices, points)
            for a, b, c in product(range(8), repeat=3):
                assert counter.count(a, b, c) == _naive(vertices, points, a, b, c)


def test_boundary_duplicates_and_order():
    vertices = [(0, 0), (8, 0), (0, 8), (8, 8), (4, 4), (0, 0)]
    points = list(product(range(-1, 10), repeat=2)) * 2 + [(1, 1)] * 3
    counter = TrianglePointCounter(vertices, points)
    for a, b, c in permutations(range(len(vertices)), 3):
        assert counter.count(a, b, c) == _naive(vertices, points, a, b, c)
    assert counter.count(0, 1, 2) == 45
    assert counter.count(0, 1, 0) == 0


def test_empty_points_and_input_copy():
    vertices = [[0, 0], [4, 0], [0, 4]]
    points = [[1, 1]]
    counter = TrianglePointCounter(iter(vertices), iter(points))
    vertices[0][0] = 100
    points[0][0] = 100
    assert counter.count(0, 1, 2) == 1
    assert TrianglePointCounter([(0, 0)], []).count(0, 0, 0) == 0
    for args in ((-1, 0, 0), (0, 1, 3)):
        with pytest.raises(IndexError):
            counter.count(*args)
    with pytest.raises(IndexError):
        TrianglePointCounter([], []).count(0, 0, 0)
