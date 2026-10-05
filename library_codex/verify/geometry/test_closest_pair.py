import random

import pytest

from library_codex.geometry.ClosestPair import closest_pair


def brute(points):
    distance, first, second = min(
        ((points[i][0] - points[j][0]) ** 2
         + (points[i][1] - points[j][1]) ** 2, i, j)
        for i in range(len(points)) for j in range(i + 1, len(points))
    )
    return first, second, distance


def test_random_against_all_pairs():
    rng = random.Random(20260820)
    for n in range(2, 65):
        for _ in range(60):
            points = [(rng.randrange(-30, 31), rng.randrange(-30, 31)) for _ in range(n)]
            assert closest_pair(points) == brute(points)


def test_large_coordinates_and_fractional_coordinates():
    rng = random.Random(105)
    for scale in (0.25, 10**9, 10**40):
        for n in (2, 3, 7, 16, 31, 65):
            points = [(rng.randrange(-100, 101) * scale,
                       rng.randrange(-100, 101) * scale) for _ in range(n)]
            assert closest_pair(points) == brute(points)


def test_equal_distances_and_duplicate_tie_break():
    rng = random.Random(106)
    for n in (2, 3, 4, 7, 15, 16, 17, 33):
        for points in (
            [(i, 0) for i in range(n)],
            [(0, i) for i in range(n)],
            [(i % 5, i // 5) for i in range(n)],
            [(i // 3, i // 3) for i in range(n)],
        ):
            rng.shuffle(points)
            assert closest_pair(points) == brute(points)


def test_generator_does_not_change_input():
    points = [[8, 3], [2, 0], [2, 1], [9, 9]]
    before = [point[:] for point in points]
    assert closest_pair(iter(points)) == brute(points)
    assert points == before


def test_close_pair_not_adjacent_in_x_order():
    points = [(i * 100, i % 13 * 100) for i in range(1025)]
    points.extend([(51150, 400), (51151, 10000), (51152, 400)])
    assert closest_pair(points) == brute(points)


def test_large_collinear_input():
    points = [(3 * i, 4 * i) for i in range(30000)]
    assert closest_pair(points) == (0, 1, 25)


@pytest.mark.parametrize("points", [[], [(0, 0)]])
def test_requires_two_points(points):
    with pytest.raises(ValueError):
        closest_pair(points)
