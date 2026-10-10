import random

import pytest

from library_codex.spatial_structure.CompressedFenwick2D import CompressedFenwick2D


def test_compressed_fenwick_2d_random():
    rng = random.Random(791350)
    points = list({
        (rng.randrange(-100, 101), rng.randrange(-100, 101))
        for _ in range(1000)
    })
    values = {point: 0 for point in points}
    solver = CompressedFenwick2D(points)
    for _ in range(10000):
        if rng.randrange(2):
            point = rng.choice(points)
            delta = rng.randrange(-30, 31)
            values[point] += delta
            solver.add(point[0], point[1], delta)
        else:
            left = rng.randrange(-110, 111)
            right = rng.randrange(left, 112)
            bottom = rng.randrange(-110, 111)
            top = rng.randrange(bottom, 112)
            expected = sum(
                value
                for (x, y), value in values.items()
                if left <= x < right and bottom <= y < top
            )
            assert solver.sum(left, bottom, right, top) == expected


def test_unregistered_point_does_not_modify_state():
    solver = CompressedFenwick2D([[0, 1], [1, 0], [0, 1]])
    solver.add(0, 1, 7)
    solver.add(1, 0, -3)
    for point in ((1, 1), (0, 0), (2, 1)):
        with pytest.raises(KeyError):
            solver.add(*point, 100)
        assert solver.prefix_sum(3, 3) == 4
    assert solver.sum(0, 1, 1, 2) == 7
    assert solver.sum(1, 0, 2, 1) == -3


def test_empty_boundaries_and_large_integers():
    assert CompressedFenwick2D([]).sum(-1, -1, 1, 1) == 0
    solver = CompressedFenwick2D([(0, 0), (1, 1)])
    solver.add(0, 0, 10**50)
    solver.add(1, 1, -10**50 + 1)
    assert solver.sum(0, 0, 1, 1) == 10**50
    assert solver.sum(0, 0, 2, 2) == 1
    assert solver.sum(0, 0, 0, 2) == 0
    assert solver.sum(0, 0, 2, 0) == 0
    assert solver.sum(2, 2, 0, 0) == 0
