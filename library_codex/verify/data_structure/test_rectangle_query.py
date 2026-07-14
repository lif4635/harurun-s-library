import random

from library_codex.data_structure.RectangleQuery import (
    CompressedFenwick2D,
    CumulativeSum2D,
    DynamicPointAddRectangleSum,
    RectangleAddRectangleSum,
    SegmentTree2D,
    StaticRectangleSum,
)


def test_dense_2d_structures_random():
    rng = random.Random(682051)
    height = 30
    width = 25
    matrix = [
        [rng.randrange(-20, 21) for _ in range(width)]
        for _ in range(height)
    ]
    cumulative = CumulativeSum2D(matrix)
    segment = SegmentTree2D(matrix, lambda first, second: first + second, 0)
    for _ in range(10000):
        if rng.randrange(4) == 0:
            row = rng.randrange(height)
            column = rng.randrange(width)
            value = rng.randrange(-20, 21)
            matrix[row][column] = value
            segment.set(row, column, value)
        else:
            top = rng.randrange(height + 1)
            bottom = rng.randrange(top, height + 1)
            left = rng.randrange(width + 1)
            right = rng.randrange(left, width + 1)
            expected = sum(sum(row[left:right]) for row in matrix[top:bottom])
            assert segment.prod(top, left, bottom, right) == expected
    original = CumulativeSum2D(
        [[row * width + column for column in range(width)] for row in range(height)]
    )
    for _ in range(1000):
        top = rng.randrange(height + 1)
        bottom = rng.randrange(top, height + 1)
        left = rng.randrange(width + 1)
        right = rng.randrange(left, width + 1)
        expected = sum(
            row * width + column
            for row in range(top, bottom)
            for column in range(left, right)
        )
        assert original.sum(top, left, bottom, right) == expected


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


def test_static_rectangle_sum_random():
    rng = random.Random(319720)
    for _ in range(100):
        solver = StaticRectangleSum()
        points = []
        for _ in range(100):
            point = (
                rng.randrange(-20, 21),
                rng.randrange(-20, 21),
                rng.randrange(-20, 21),
            )
            points.append(point)
            solver.add(*point)
        expected = []
        for _ in range(100):
            left = rng.randrange(-25, 26)
            right = rng.randrange(left, 27)
            bottom = rng.randrange(-25, 26)
            top = rng.randrange(bottom, 27)
            solver.query(left, bottom, right, top)
            expected.append(sum(
                value
                for x, y, value in points
                if left <= x < right and bottom <= y < top
            ))
        assert solver.solve() == expected


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
