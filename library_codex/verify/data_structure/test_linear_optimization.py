import random

from library_codex.spatial_structure.LineContainer2D import LineContainer2D


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
