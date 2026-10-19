import itertools
import random

from library_codex.geometry.ConvexHull import convex_hull
from library_codex.geometry.ConvexLayers import _DecrementalHull, convex_layers, onion_depth


def brute(points, keep):
    remaining = set(points)
    result = []
    while remaining:
        layer = convex_hull(remaining, keep)
        result.append(layer)
        remaining.difference_update(layer)
    return result


def check(points):
    before = points[:]
    for keep in (False, True):
        expected = brute(points, keep)
        assert convex_layers(points, keep) == expected
        depths = {point: i for i, layer in enumerate(expected) for point in layer}
        assert onion_depth(points, keep) == [depths[p] for p in points]
    assert points == before


def test_boundaries():
    for points in ([], [(1, 2)], [(1, 2)] * 5, [(2, 3), (0, 1)],
                   [(0, 0), (4, 0), (4, 4), (0, 4), (1, 1), (3, 1), (3, 3), (1, 3), (2, 2)]):
        check(points)
    for dx, dy in ((1, 0), (0, 1), (2, -3)):
        check([(dx * t + 7, dy * t - 11) for t in range(-40, 40)])
    assert onion_depth([(0, 0), (2, 2), (1, 1)]) == [0, 0, 0]


def test_exhaustive_grid():
    grid = list(itertools.product(range(3), repeat=2))
    for mask in range(1 << len(grid)):
        check([p for i, p in enumerate(grid) if mask >> i & 1])


def test_random():
    rng = random.Random(23876)
    for n in range(1, 100):
        for _ in range(12):
            check([(rng.randrange(-20, 21), rng.randrange(-20, 21)) for _ in range(n)])


def test_large_coordinates_and_affine_transforms():
    rng = random.Random(7589)
    for _ in range(30):
        points = [(rng.randrange(-100, 101), rng.randrange(-100, 101)) for _ in range(70)]
        check([(10**30 + x * 10**20 + y, -10**40 + y * 10**20) for x, y in points])


def test_nested_and_parabolic():
    check([(sx * r, sy * r) for r in range(1, 90) for sx, sy in itertools.product((-1, 1), repeat=2)])
    check([(x, x * x) for x in range(-90, 91)])
    check(list(itertools.product(range(20), repeat=2)))


def test_arbitrary_deletions():
    rng = random.Random(98653)
    for _ in range(40):
        points = sorted(set((rng.randrange(50), rng.randrange(50)) for _ in range(100)), key=lambda p: (p[1], p[0]))
        hull = _DecrementalHull(points)
        remaining = set(range(len(points)))
        while remaining:
            expected = []
            for i in sorted(remaining):
                x, y = points[i]
                while len(expected) >= 2:
                    ax, ay = points[expected[-2]]
                    bx, by = points[expected[-1]]
                    if (bx - ax) * (y - ay) <= (by - ay) * (x - ax):
                        break
                    expected.pop()
                expected.append(i)
            assert hull.hull() == expected
            removed = rng.sample(sorted(remaining), min(len(remaining), rng.randrange(1, 6)))
            hull.erase(removed)
            remaining.difference_update(removed)
        assert hull.hull() == []
