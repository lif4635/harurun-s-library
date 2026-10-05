import itertools
import math
from library_codex.geometry.PolygonMetrics import (
    pick_lattice_points,
    polygon_centroid,
    signed_doubled_area,
)


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
