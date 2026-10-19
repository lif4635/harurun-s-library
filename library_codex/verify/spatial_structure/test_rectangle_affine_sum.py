import random

import pytest

from library_codex.spatial_structure.RectangleAffineSum import RectangleAffineSum


def test_random_affine_activation_and_set():
    rng = random.Random(6893)
    for mod in (1, 12, 998244353):
        for n in (0, 1, 2, 15, 31, 32, 33, 100):
            points = [(rng.randrange(-4, 5), rng.randrange(-4, 5), rng.choice((None, 0, 3))) for _ in range(n)]
            values = [w if w is None else w % mod for x, y, w in points]
            tree = RectangleAffineSum(points, mod)
            for _ in range(200):
                if n and rng.randrange(3) == 0:
                    i = rng.randrange(n)
                    w = rng.choice((None, rng.randrange(-10, 20)))
                    tree.set(i, w)
                    values[i] = w if w is None else w % mod
                    assert tree.get(i) == values[i]
                else:
                    l, r = sorted((rng.randrange(-5, 6), rng.randrange(-5, 6)))
                    d, u = sorted((rng.randrange(-5, 6), rng.randrange(-5, 6)))
                    selected = [i for i, (x, y, _) in enumerate(points) if l <= x < r and d <= y < u and values[i] is not None]
                    if rng.randrange(2):
                        a, b = rng.randrange(-5, 10), rng.randrange(-10, 20)
                        tree.apply(l, r, d, u, a, b)
                        for i in selected:
                            values[i] = (a * values[i] + b) % mod
                    else:
                        assert tree.sum(l, r, d, u) == sum(values[i] for i in selected) % mod
                if rng.randrange(20) == 0:
                    assert tree.tolist() == values
                    assert str(tree) == str(values)
                    current = [(x, y, values[i]) for i, (x, y, _) in enumerate(points)]
                    assert repr(tree) == "RectangleAffineSum(%r, mod=%r)" % (current, mod)
            assert tree.tolist() == values
            assert all(isinstance(value, int) for value in tree._values)


def test_inactive_points_and_half_open_boundaries():
    tree = RectangleAffineSum([(0, 0, 2), (0, 0, None), (1, 0, 3), (0, 1, 4)])
    tree.apply(-1, 2, -1, 2, 0, 10)
    tree.set(1, 7)
    assert tree.sum(0, 1, 0, 1) == 17
    assert tree.tolist() == [10, 7, 10, 10]
    tree.set(0, None)
    tree.apply(-1, 2, -1, 2, 3, 1)
    tree.set(0, 5)
    assert tree.tolist() == [5, 22, 31, 31]
    assert tree.sum(0, 2, 0, 2) == 89
    tree.tolist()[0] = 0
    assert tree.get(0) == 5
    assert tree.sum(0, 0, 0, 1) == 0


def test_invalid_arguments():
    with pytest.raises(ValueError):
        RectangleAffineSum([], 0)
    tree = RectangleAffineSum([(0, 0, 1)])
    for i in (-1, 1):
        with pytest.raises(IndexError):
            tree.get(i)
        with pytest.raises(IndexError):
            tree.set(i, 1)
    with pytest.raises(ValueError):
        tree.sum(1, 0, 0, 1)
    with pytest.raises(ValueError):
        tree.apply(0, 1, 1, 0, 1, 0)


def test_thin_grid_and_coincident_coordinates():
    rng = random.Random(89642)
    for swapped in (False, True):
        points = [(i * 103, i % 7, i) if not swapped else (i % 7, i * 103, i) for i in range(1000)]
        points.extend([(0, 0, None)] * 100)
        tree = RectangleAffineSum(points)
        weights = [p[2] for p in points]
        for _ in range(100):
            l, r = sorted((rng.randrange(-1, 103001), rng.randrange(-1, 103001)))
            d, u = sorted((rng.randrange(-1, 8), rng.randrange(-1, 8)))
            if swapped:
                l, r, d, u = d, u, l, r
            a, b = rng.randrange(5), rng.randrange(10)
            tree.apply(l, r, d, u, a, b)
            for i, (x, y, _) in enumerate(points):
                if weights[i] is not None and l <= x < r and d <= y < u:
                    weights[i] = (a * weights[i] + b) % 998244353
            assert tree.tolist() == weights
            assert tree.sum(l, r, d, u) == sum(w for (x, y, _), w in zip(points, weights) if w is not None and l <= x < r and d <= y < u) % 998244353
