import itertools
import math
import random

from library_codex.geometry.Delaunay import delaunay_edges


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def check(points):
    before = points[:]
    edges = delaunay_edges(points)
    assert points == before
    assert len(set(tuple(sorted(e)) for e in edges)) == len(edges)
    n = len(points)
    graph = [[] for _ in points]
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n and u != v
        graph[u].append(v)
        graph[v].append(u)
    reached = {0} if n else set()
    stack = list(reached)
    while stack:
        for v in graph[stack.pop()]:
            if v not in reached:
                reached.add(v)
                stack.append(v)
    assert len(reached) == n
    if n < 3:
        assert len(edges) == max(0, n - 1)
        return
    assert len(edges) <= 3 * n - 6
    for u, v in edges:
        a, b = points[u], points[v]
        for i, p in enumerate(points):
            if i not in (u, v) and cross(a, b, p) == 0:
                assert not (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
                            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
        for s, t in edges:
            c, d = points[s], points[t]
            assert not (cross(a, b, c) * cross(a, b, d) < 0
                        and cross(c, d, a) * cross(c, d, b) < 0)
    for u, neighbors in enumerate(graph):
        x, y = points[u]
        neighbors.sort(key=lambda v: math.atan2(points[v][1] - y, points[v][0] - x))
    visited = set()
    positive = 0
    for u, neighbors in enumerate(graph):
        for v in neighbors:
            if (u, v) in visited:
                continue
            a, b = u, v
            face = []
            while (a, b) not in visited:
                visited.add((a, b))
                face.append(a)
                row = graph[b]
                a, b = b, row[row.index(a) - 1]
            assert (a, b) == (u, v)
            area = sum(points[a][0] * points[b][1] - points[a][1] * points[b][0]
                       for a, b in zip(face, face[1:] + face[:1]))
            if area <= 0:
                continue
            positive += 1
            assert len(face) == 3
            for d in points:
                (ax, ay), (bx, by), (cx, cy) = [(points[i][0] - d[0], points[i][1] - d[1]) for i in face]
                determinant = ((ax * ax + ay * ay) * (bx * cy - by * cx)
                               + (bx * bx + by * by) * (cx * ay - cy * ax)
                               + (cx * cx + cy * cy) * (ax * by - ay * bx))
                assert determinant <= 0
    assert positive == len(edges) - n + 1


def test_grid_subsets():
    grid = list(itertools.product(range(3), repeat=2))
    for mask in range(1 << len(grid)):
        check([p for i, p in enumerate(grid) if mask >> i & 1])


def test_random_and_permutations():
    rng = random.Random(20901)
    for _ in range(150):
        points = sorted({(rng.randrange(-100, 101), rng.randrange(-100, 101)) for _ in range(25)})
        check(points)
        rng.shuffle(points)
        check(points)


def test_collinear_cocircular_and_duplicates():
    check([(i * 7, i * -3) for i in range(-10, 11)])
    check([(0, 5), (3, 4), (5, 0), (3, -4), (0, -5), (-3, -4), (-5, 0), (-3, 4)])
    points = [(2, 2), (0, 0), (2, 2), (0, 0), (4, 0), (2, 2)]
    edges = {tuple(sorted(e)) for e in delaunay_edges(points)}
    assert {(0, 2), (0, 5), (1, 3)} <= edges
    assert edges - {(0, 2), (0, 5), (1, 3)} == {(0, 1), (0, 4), (1, 4)}
    assert len(delaunay_edges([(0, 0)] * 100)) == 99


def test_large_integer_predicates():
    rng = random.Random(91801)
    points = [(rng.randrange(-100, 101), rng.randrange(-100, 101)) for _ in range(25)]
    expected = {tuple(sorted(e)) for e in delaunay_edges(points)}
    shifted = [(10**70 + x * 10**30, -10**80 + y * 10**30) for x, y in points]
    assert {tuple(sorted(e)) for e in delaunay_edges(shifted)} == expected
