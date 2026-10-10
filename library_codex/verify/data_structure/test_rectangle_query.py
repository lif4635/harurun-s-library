import random

from library_codex.spatial_structure.CumulativeSum2D import CumulativeSum2D
from library_codex.spatial_structure.SegmentTree2D import SegmentTree2D
from library_codex.spatial_structure.StaticRectangleSum import StaticRectangleSum


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
