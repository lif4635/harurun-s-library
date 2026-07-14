import random

from library_codex.data_structure.RectangleQuery import PointUpdateRangeTree2D


def test_point_update_range_tree_against_brute_sum():
    rng = random.Random(121)
    for size in range(1, 100):
        points = list({(rng.randrange(-30, 31), rng.randrange(-30, 31))
                      for _ in range(size)})
        tree = PointUpdateRangeTree2D(points).build()
        values = {point: 0 for point in points}
        for _ in range(1000):
            if rng.randrange(2):
                point = rng.choice(points)
                delta = rng.randrange(-100, 101)
                tree.add(*point, delta)
                values[point] += delta
            else:
                x1, x2 = sorted((rng.randrange(-35, 36), rng.randrange(-35, 36)))
                y1, y2 = sorted((rng.randrange(-35, 36), rng.randrange(-35, 36)))
                expected = sum(value for (x, y), value in values.items()
                               if x1 <= x < x2 and y1 <= y < y2)
                assert tree.query(x1, y1, x2, y2) == expected


def test_range_tree_generic_x_ordered_concatenation():
    points = [(x, 0) for x in range(30)]
    tree = PointUpdateRangeTree2D(
        points,
        op=lambda first, second: first + second,
        identity="",
    ).build()
    for x in range(30):
        tree.add(x, 0, chr(65 + x % 26))
    for left in range(31):
        for right in range(left, 31):
            assert tree.query(left, 0, right, 1) == "".join(
                chr(65 + x % 26) for x in range(left, right)
            )
