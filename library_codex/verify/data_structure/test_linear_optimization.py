import random

from library_codex.data_structure.LinearOptimization import (
    LineContainer2D,
    RangeLinearAddRangeMin,
)


def test_line_container_2d_against_brute_force():
    rng = random.Random(919)
    points = []
    container = LineContainer2D()
    for _ in range(1000):
        if not points or rng.randrange(3) == 0:
            point = rng.randrange(-10 ** 9, 10 ** 9), rng.randrange(-10 ** 9, 10 ** 9)
            points.append(point)
            container.add(*point)
        else:
            a = rng.randrange(-10 ** 9, 10 ** 9)
            b = rng.randrange(-10 ** 9, 10 ** 9)
            values = [a * x + b * y for x, y in points]
            assert container.max_ll(a, b) == max(values)
            assert container.min_ll(a, b) == min(values)


def test_range_linear_add_range_min_against_brute_force():
    rng = random.Random(202407)
    for size in range(1, 70):
        values = [rng.randrange(-1000, 1001) for _ in range(size)]
        tree = RangeLinearAddRangeMin(values)
        for _ in range(800):
            left = rng.randrange(size)
            right = rng.randrange(left + 1, size + 1)
            if rng.randrange(3):
                slope = rng.randrange(-100, 101)
                intercept = rng.randrange(-1000, 1001)
                tree.update(left, right, slope, intercept)
                for index in range(left, right):
                    values[index] += slope * index + intercept
            else:
                assert tree.query(left, right) == min(values[left:right])

