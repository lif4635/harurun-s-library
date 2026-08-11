import itertools
import math
import random

import pytest

from library_codex.geometry.ClosestPair import closest_pair
from library_codex.geometry.PolygonMetrics import (
    pick_lattice_points,
    polygon_centroid,
    signed_doubled_area,
)


def test_closest_pair_random_against_all_pairs():
    random.seed(20260820)
    for n in range(2, 45):
        for _ in range(60):
            points = [(random.randrange(-30, 31), random.randrange(-30, 31))
                      for _ in range(n)]
            first, second, distance = closest_pair(points)
            expected = min(
                ((points[i][0] - points[j][0]) ** 2
                 + (points[i][1] - points[j][1]) ** 2, i, j)
                for i in range(n) for j in range(i + 1, n)
            )
            assert (distance, first, second) == expected
    with pytest.raises(ValueError):
        closest_pair([(0, 0)])


def test_polygon_metrics_orientation_centroid_and_pick():
    rectangle = [(0, 0), (6, 0), (6, 4), (0, 4)]
    assert signed_doubled_area(rectangle) == 48
    assert signed_doubled_area(list(reversed(rectangle))) == -48
    assert polygon_centroid(rectangle) == (3, 2)
    assert polygon_centroid(list(reversed(rectangle))) == (3, 2)
    assert pick_lattice_points(rectangle) == (20, 15)
    triangle = [(0, 0), (4, 0), (0, 3)]
    cx, cy = polygon_centroid(triangle)
    assert math.isclose(cx, 4 / 3)
    assert math.isclose(cy, 1)
    assert pick_lattice_points(triangle) == (8, 3)
