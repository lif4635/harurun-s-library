from fractions import Fraction
from itertools import combinations
from math import dist, isclose
from random import Random

import pytest

from library_codex.geometry.MinimumEnclosingCircle import minimum_enclosing_circle, minimum_enclosing_circle_boundary


def brute_circle(points):
    candidates = [(Fraction(x), Fraction(y)) for x, y in points]
    for a, b in combinations(points, 2):
        candidates.append((Fraction(a[0] + b[0], 2), Fraction(a[1] + b[1], 2)))
    for a, b, c in combinations(points, 3):
        ux, uy = b[0] - a[0], b[1] - a[1]
        vx, vy = c[0] - a[0], c[1] - a[1]
        determinant = ux * vy - uy * vx
        if determinant:
            u = (b[0] ** 2 + b[1] ** 2 - a[0] ** 2 - a[1] ** 2)
            v = (c[0] ** 2 + c[1] ** 2 - a[0] ** 2 - a[1] ** 2)
            candidates.append((Fraction(u * vy - v * uy, 2 * determinant), Fraction(ux * v - vx * u, 2 * determinant)))
    return min((max((x - a) ** 2 + (y - b) ** 2 for a, b in points), x, y) for x, y in candidates)


def test_circle_and_boundary_against_rational_enumeration():
    rng = Random(20261015)
    for n in range(1, 9):
        for _ in range(50):
            points = [(rng.randrange(-5, 6), rng.randrange(-5, 6)) for _ in range(n)]
            before = points[:]
            squared, x, y = brute_circle(points)
            expected = [int((a - x) ** 2 + (b - y) ** 2 == squared) for a, b in points]
            for seed in (0, 1, 17):
                assert minimum_enclosing_circle_boundary(points, seed) == expected
            center, radius, support = minimum_enclosing_circle(points)
            assert 1 <= len(support) <= 3
            assert all(dist(center, point) <= radius + 1e-8 for point in points)
            assert isclose(radius ** 2, float(squared), abs_tol=1e-8)
            assert points == before


@pytest.mark.parametrize("points,expected", [
    ([(0, 0)], [1]),
    ([(1, 1)] * 5, [1] * 5),
    ([(0, 0), (1, 0), (2, 0), (2, 0)], [1, 0, 1, 1]),
    ([(5, 0), (0, 5), (-5, 0), (0, -5), (3, 4), (0, 0)], [1, 1, 1, 1, 1, 0]),
    ([(-10**18, 0), (10**18, 0), (0, 10**18), (0, 10**18-1)], [1, 1, 1, 0]),
])
def test_boundary_exact_cases(points, expected):
    assert minimum_enclosing_circle_boundary(points) == expected
    shifted = [(x + 10**30, y - 10**30) for x, y in points]
    assert minimum_enclosing_circle_boundary(shifted) == expected


def test_invalid_input():
    with pytest.raises(ValueError):
        minimum_enclosing_circle([])
    with pytest.raises(ValueError):
        minimum_enclosing_circle_boundary([])
    with pytest.raises(TypeError):
        minimum_enclosing_circle_boundary([(0.5, 1)])
