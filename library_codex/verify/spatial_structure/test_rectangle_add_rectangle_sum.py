import random

import pytest

from library_codex.spatial_structure.RectangleAddRectangleSum import RectangleAddRectangleSum


def test_rectangle_add_rectangle_sum_random_integer_area():
    rng = random.Random(591027)
    for _ in range(100):
        solver = RectangleAddRectangleSum()
        rectangles = []
        for _ in range(100):
            left = rng.randrange(-15, 16)
            right = rng.randrange(left, 17)
            bottom = rng.randrange(-15, 16)
            top = rng.randrange(bottom, 17)
            value = rng.randrange(-10, 11)
            solver.add(left, bottom, right, top, value)
            rectangles.append((left, bottom, right, top, value))
        expected = []
        for _ in range(100):
            left = rng.randrange(-17, 18)
            right = rng.randrange(left, 19)
            bottom = rng.randrange(-17, 18)
            top = rng.randrange(bottom, 19)
            solver.query(left, bottom, right, top)
            total = 0
            for xl, yb, xr, yt, value in rectangles:
                overlap_x = max(0, min(right, xr) - max(left, xl))
                overlap_y = max(0, min(top, yt) - max(bottom, yb))
                total += overlap_x * overlap_y * value
            expected.append(total)
        assert solver.solve() == expected
        for mod in (1, 12, 998244353):
            assert solver.solve(mod) == [value % mod for value in expected]


def test_boundaries_large_values_and_repeat():
    solver = RectangleAddRectangleSum()
    solver.query(0, 0, 10**9, 10**9)
    solver.add(0, 0, 10**9, 10**9, -(10**30))
    solver.add(0, 0, 0, 10**9, 5)
    solver.query(10**9, 0, 10**9 + 1, 1)
    solver.query(0, 0, 0, 1)
    assert solver.solve() == [-10**48, 0, 0]
    assert solver.solve(998244353) == [(-10**48) % 998244353, 0, 0]
    assert solver.solve() == [-10**48, 0, 0]
    assert RectangleAddRectangleSum().solve() == []
    for mod in (0, -1):
        with pytest.raises(ValueError):
            solver.solve(mod)
