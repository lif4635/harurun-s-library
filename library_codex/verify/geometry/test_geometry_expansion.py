import random

import pytest

from library_codex.geometry.ConvexHull import convex_hull
from library_codex.geometry.FurthestPair import furthest_pair
from library_codex.geometry.MinkowskiSum import minkowski_sum
from library_codex.geometry.PointInPolygon import point_location


def test_point_location_boundary_and_concavity():
    polygon = [(0, 0), (5, 0), (5, 5), (3, 2), (0, 5)]
    assert point_location(polygon, (1, 1)) == 1
    assert point_location(polygon, (4, 4)) == -1
    assert point_location(polygon, (4, 3.5)) == 0
    assert point_location(polygon, (0, 0)) == 0
    assert point_location([], (0, 0)) == -1


def test_minkowski_random_against_all_pair_sums():
    random.seed(20260816)
    for _ in range(600):
        first = convex_hull([
            (random.randrange(-5, 6), random.randrange(-5, 6))
            for _ in range(random.randrange(1, 10))
        ])
        second = convex_hull([
            (random.randrange(-5, 6), random.randrange(-5, 6))
            for _ in range(random.randrange(1, 10))
        ])
        expected = convex_hull([
            (a[0] + b[0], a[1] + b[1]) for a in first for b in second
        ])
        assert minkowski_sum(first, second) == expected
        assert minkowski_sum(list(reversed(first)), second) == expected


def test_furthest_pair_random_against_all_pairs():
    random.seed(20260818)
    for n in range(1, 30):
        for _ in range(100):
            points = [(random.randrange(-12, 13), random.randrange(-12, 13)) for _ in range(n)]
            first, second, distance = furthest_pair(points)
            expected = max(
                (sum((points[i][axis] - points[j][axis]) ** 2 for axis in range(2)),
                 (-min(i, j), -max(i, j)))
                for i in range(n) for j in range(i, n)
            )[0]
            assert distance == expected
            assert sum((points[first][axis] - points[second][axis]) ** 2 for axis in range(2)) == distance
    with pytest.raises(ValueError):
        furthest_pair([])
