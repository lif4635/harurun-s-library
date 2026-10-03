import random

from library_codex.geometry.ConvexFurthest import furthest_neighbors
from library_codex.geometry.ConvexHull import convex_hull


def check(points):
    original = points[:]
    result = furthest_neighbors(points)
    assert points == original
    assert len(result) == len(points)
    for i, j in enumerate(result):
        x, y = points[i]
        expected = max((x - a) ** 2 + (y - b) ** 2 for a, b in points)
        a, b = points[j]
        assert (x - a) ** 2 + (y - b) ** 2 == expected


def test_empty_small_and_symmetric():
    assert furthest_neighbors([]) == []
    assert furthest_neighbors([(4, 2)]) == [0]
    assert furthest_neighbors([(1, 0), (-1, 0)]) == [1, 0]
    for points in (
        [(0, 0), (4, 0), (4, 3), (0, 3)],
        [(0, 0), (2, 1), (2, 3), (0, 4), (-2, 3), (-2, 1)],
        [(-10**9, -10**9), (10**9, -10**9), (10**9, 10**9), (-10**9, 10**9)],
    ):
        check(points)
        check(points[::-1])


def test_random_hulls_against_all_pairs():
    rng = random.Random(420)
    for _ in range(1000):
        points = convex_hull([(rng.randrange(-100, 101), rng.randrange(-100, 101)) for _ in range(rng.randrange(3, 150))])
        check(points)
        check(points[::-1])


def test_long_thin_polygon():
    points = [(i, i * i) for i in range(-250, 251)]
    check(points)


def test_non_unimodal_distances():
    points = [(0, 0), (-18767, -43052), (-21874, -41502), (-100000, 0), (-280, 6810), (-189, 4855)]
    for offset in range(len(points)):
        rotated = points[offset:] + points[:offset]
        check(rotated)
        check(rotated[::-1])
