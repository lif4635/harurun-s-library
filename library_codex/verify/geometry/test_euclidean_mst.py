import itertools
import random

from library_codex.geometry.EuclideanMST import euclidean_mst


def check(points):
    n = len(points)
    expected = []
    distance = [None] * n
    used = bytearray(n)
    if n:
        distance[0] = 0
    for _ in range(n):
        u = min((i for i in range(n) if not used[i] and distance[i] is not None), key=lambda i: distance[i])
        expected.append(distance[u])
        used[u] = 1
        for v in range(n):
            d = (points[u][0] - points[v][0]) ** 2 + (points[u][1] - points[v][1]) ** 2
            if not used[v] and (distance[v] is None or d < distance[v]):
                distance[v] = d
    before = points[:]
    edges = euclidean_mst(points)
    assert points == before
    assert len(edges) == max(0, n - 1)
    parent = list(range(n))
    actual = []
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n
        a, b = u, v
        while parent[a] != a:
            a = parent[a]
        while parent[b] != b:
            b = parent[b]
        assert a != b
        parent[a] = b
        actual.append((points[u][0] - points[v][0]) ** 2 + (points[u][1] - points[v][1]) ** 2)
    assert actual == sorted(expected[1:])


def test_boundaries():
    for points in ([], [(0, 0)], [(3, 7)] * 20, [(0, 0), (1, 1)], [(0, 0), (1, 0), (2, 0)]):
        check(points)
    for dx, dy in ((1, 0), (0, 1), (5, -2)):
        check([(dx * i, dy * i) for i in range(-30, 30)])


def test_grid_subsets():
    grid = list(itertools.product(range(3), repeat=2))
    for mask in range(1 << 9):
        check([grid[i] for i in range(9) if mask >> i & 1])


def test_random():
    rng = random.Random(83723)
    for n in range(1, 100):
        for _ in range(10):
            check([(rng.randrange(-40, 41), rng.randrange(-40, 41)) for _ in range(n)])


def test_cocircular_and_large_integers():
    circle = [(5, 0), (4, 3), (3, 4), (0, 5), (-3, 4), (-4, 3), (-5, 0), (-4, -3), (-3, -4), (0, -5), (3, -4), (4, -3)]
    check(circle)
    check([(x * r, y * r) for r in range(1, 8) for x, y in circle])
    check([(10**40 + x * 10**30, -10**50 + y * 10**30) for x, y in circle])
