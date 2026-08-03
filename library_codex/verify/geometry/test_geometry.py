import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.geometry.ArgumentSort import argument_sort  # noqa: E402
from library_codex.geometry.ConvexHull import convex_hull  # noqa: E402
from library_codex.geometry.Orientation import cross, orientation  # noqa: E402
from library_codex.geometry.SegmentIntersection import segments_intersect  # noqa: E402


def test_orientation_and_segment_intersection():
    assert cross((0, 0), (2, 0), (1, 3)) == 6
    assert orientation((0, 0), (2, 0), (1, 3)) == 1
    assert orientation((0, 0), (1, 1), (2, 2)) == 0
    assert orientation((0, 0), (1, 0), (1, -1)) == -1
    assert segments_intersect((0, 0), (4, 4), (0, 4), (4, 0))
    assert segments_intersect((0, 0), (2, 0), (2, 0), (4, 0))
    assert not segments_intersect(
        (0, 0), (2, 0), (2, 0), (4, 0), touch=False
    )
    assert segments_intersect((0, 0), (4, 0), (1, 0), (3, 0))
    assert not segments_intersect((0, 0), (1, 0), (2, 0), (3, 0))


def test_convex_hull_and_argument_sort_random():
    points = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 1), (1, 0), (0, 0)]
    assert convex_hull(points) == [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert convex_hull([(0, 0), (1, 0), (2, 0)], keep_collinear=True) == [
        (0, 0), (1, 0), (2, 0)
    ]

    rng = random.Random(410)
    for _ in range(200):
        points = [(rng.randrange(-20, 21), rng.randrange(-20, 21))
                  for _ in range(30)]
        hull = convex_hull(points)
        if len(hull) >= 3:
            for first, second in zip(hull, hull[1:] + hull[:1]):
                assert all(cross(first, second, point) >= 0 for point in points)

        vectors = [(x, y) for x, y in points if x or y]
        ordered = argument_sort(vectors)
        angles = [math.atan2(y, x) % (2 * math.pi) for x, y in ordered]
        assert angles == sorted(angles)
        assert sorted(ordered) == sorted(vectors)
