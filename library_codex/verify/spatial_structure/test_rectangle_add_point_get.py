import random

import pytest

from library_codex.spatial_structure.RectangleAddPointGet import RectangleAddPointGet


def test_random_against_direct_updates():
    rng = random.Random(972661)
    for _ in range(100):
        points = list({(rng.randrange(-10, 11), rng.randrange(-10, 11)) for _ in range(60)})
        solver = RectangleAddPointGet(iter(points + points[:5]))
        values = dict.fromkeys(points, 0)
        for _ in range(200):
            left, right = sorted((rng.randrange(-12, 13), rng.randrange(-12, 13)))
            bottom, top = sorted((rng.randrange(-12, 13), rng.randrange(-12, 13)))
            value = rng.randrange(-100, 101)
            solver.add(left, bottom, right, top, value)
            for x, y in points:
                if left <= x < right and bottom <= y < top:
                    values[x, y] += value
            point = rng.choice(points)
            assert solver.get(*point) == values[point]
        expected = [(x, y, values[x, y]) for x, y in sorted(points)]
        assert solver.items() == expected
        assert str(solver) == str(expected)
        assert repr(solver) == f"RectangleAddPointGet({expected!r})"
        assert solver.items() == expected


def test_empty_edges_and_unregistered_points():
    empty = RectangleAddPointGet([])
    empty.add(-10, -10, 10, 10, 7)
    assert empty.items() == []
    solver = RectangleAddPointGet([[0, 0], [0, 1], [1, 0], [1, 1]])
    solver.add(0, 0, 1, 1, 10**50)
    assert solver.items() == [(0, 0, 10**50), (0, 1, 0), (1, 0, 0), (1, 1, 0)]
    solver.add(-1, -1, 2, 2, -7)
    solver.add(0, 0, 0, 2, 99)
    solver.add(2, 2, 0, 0, 99)
    assert solver.get(0, 0) == 10**50 - 7
    for point in ((2, 1), (1, 2)):
        with pytest.raises(KeyError):
            solver.get(*point)
