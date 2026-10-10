import random

from library_codex.spatial_structure.DynamicPointAddRectangleSum import DynamicPointAddRectangleSum


def test_dynamic_point_add_rectangle_sum_operation_order():
    rng = random.Random(751920)
    solver = DynamicPointAddRectangleSum()
    points = {}
    expected = []
    for _ in range(5000):
        if rng.randrange(2):
            x = rng.randrange(-30, 31)
            y = rng.randrange(-30, 31)
            value = rng.randrange(-20, 21)
            solver.add(x, y, value)
            points[(x, y)] = points.get((x, y), 0) + value
        else:
            left = rng.randrange(-35, 36)
            right = rng.randrange(left, 37)
            bottom = rng.randrange(-35, 36)
            top = rng.randrange(bottom, 37)
            solver.query(left, bottom, right, top)
            expected.append(sum(
                value
                for (x, y), value in points.items()
                if left <= x < right and bottom <= y < top
            ))
    assert solver.solve() == expected
