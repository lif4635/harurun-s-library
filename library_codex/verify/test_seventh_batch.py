import random

from library_codex.geometry.ConvexLayers import convex_layers, onion_depth
from library_codex.geometry.LineGeometry import (
    distance_to_line,
    line_intersection,
    projection,
    reflection,
)
from library_codex.graph.EulerianTrail import eulerian_trail
from library_codex.graph_enumeration.MinimumCostCycle import minimum_cost_cycle
from library_codex.range_query.StaticRangeFrequency import StaticRangeFrequency
from library_codex.string.StringSearch import kmp_search, prefix_function
from library_codex.tree.SubtreeDiameter import subtree_diameters
from library_codex.tree_query.TreeMo import TreeMo
from library_codex.tree_query.TreeMonoid import TreeMonoid
from library_codex.union_find.WeightedUnionFind import RollbackWeightedUnionFind


def path_vertices(tree, first, second):
    parent = {first: -1}
    queue = [first]
    for vertex in queue:
        if vertex == second:
            break
        for other in tree[vertex]:
            if other not in parent:
                parent[other] = vertex
                queue.append(other)
    result = []
    vertex = second
    while vertex >= 0:
        result.append(vertex)
        vertex = parent[vertex]
    return result[::-1]


def test_kmp_random():
    rng = random.Random(81420)
    for n in range(40):
        for m in range(12):
            text = [rng.randrange(4) for _ in range(n)]
            pattern = [rng.randrange(4) for _ in range(m)]
            expected = [i for i in range(n - m + 1) if text[i:i + m] == pattern]
            assert kmp_search(text, pattern) == expected
    assert prefix_function("ababa") == [0, 0, 1, 2, 3]


def test_eulerian_trail_lexicographic():
    edges = [(0, 2), (0, 1), (1, 0), (2, 0)]
    vertices, _ = eulerian_trail(3, edges, True, 0, lexicographic=True)
    assert vertices == [0, 1, 0, 2, 0]


def test_rollback_weighted_union_find():
    solver = RollbackWeightedUnionFind(5)
    initial = solver.snapshot()
    assert solver.merge(0, 1, 4)
    assert solver.merge(1, 2, -7)
    middle = solver.snapshot()
    assert solver.diff(0, 2) == -3
    assert solver.merge(2, 3, 9)
    assert solver.diff(0, 3) == 6
    assert not solver.merge(0, 3, 5)
    solver.rollback(middle)
    assert solver.diff(0, 2) == -3
    assert solver.diff(0, 3) is None
    solver.rollback(initial)
    assert solver.component_count == 5


def test_static_range_frequency_random():
    rng = random.Random(91803)
    values = [rng.randrange(12) for _ in range(300)]
    solver = StaticRangeFrequency(values)
    for _ in range(3000):
        left = rng.randrange(301)
        right = rng.randrange(left, 301)
        value = rng.randrange(12)
        assert solver.count(value, left, right) == values[left:right].count(value)
    for value in range(12):
        positions = [i for i, current in enumerate(values) if current == value]
        assert solver.positions(value) == tuple(positions)
        for k, position in enumerate(positions):
            assert solver.kth(value, k) == position


def test_tree_mo_and_tree_monoid_random():
    rng = random.Random(512709)
    for n in range(1, 60):
        tree = [[] for _ in range(n)]
        for vertex in range(1, n):
            parent = rng.randrange(vertex)
            tree[parent].append(vertex)
            tree[vertex].append(parent)
        values = [chr(97 + rng.randrange(5)) for _ in range(n)]
        monoid = TreeMonoid(tree, lambda a, b: a + b, "", values)
        tree_mo = TreeMo(tree, query_count=100)
        queries = []
        for _ in range(100):
            first = rng.randrange(n)
            second = rng.randrange(n)
            queries.append((first, second))
            tree_mo.add_query(first, second)
            path = path_vertices(tree, first, second)
            assert monoid.path_prod(first, second) == "".join(values[v] for v in path)

        active_sum = 0

        def add(vertex):
            nonlocal active_sum
            active_sum += vertex + 1

        def remove(vertex):
            nonlocal active_sum
            active_sum -= vertex + 1

        answers = tree_mo.run(add, remove, lambda: active_sum)
        expected = [sum(v + 1 for v in path_vertices(tree, u, v)) for u, v in queries]
        assert answers == expected


def test_subtree_diameter_random():
    rng = random.Random(902841)
    for n in range(1, 50):
        tree = [[] for _ in range(n)]
        parent = [-1] * n
        for vertex in range(1, n):
            par = rng.randrange(vertex)
            weight = rng.randrange(1, 10)
            parent[vertex] = par
            tree[par].append((vertex, weight))
            tree[vertex].append((par, weight))
        result = subtree_diameters(tree)
        for root, (distance, first, second) in enumerate(result):
            descendants = [v for v in range(n) if v == root or root in ancestors(parent, v)]
            assert first in descendants and second in descendants
            expected = 0
            for start in descendants:
                stack = [(start, -1, 0)]
                while stack:
                    vertex, par, current = stack.pop()
                    if vertex in descendants:
                        expected = max(expected, current)
                    for other, weight in tree[vertex]:
                        if other != par and other in descendants:
                            stack.append((other, vertex, current + weight))
            assert distance == expected


def ancestors(parent, vertex):
    result = []
    while parent[vertex] >= 0:
        vertex = parent[vertex]
        result.append(vertex)
    return result


def test_geometry_helpers():
    points = [(0, 0), (4, 0), (4, 4), (0, 4), (1, 1), (3, 1), (3, 3), (1, 3), (2, 2)]
    layers = convex_layers(points)
    assert set(layers[0]) == {(0, 0), (4, 0), (4, 4), (0, 4)}
    assert set(layers[1]) == {(1, 1), (3, 1), (3, 3), (1, 3)}
    assert layers[2] == [(2, 2)]
    assert onion_depth([(0, 0), (2, 2), (1, 1)]) == [0, 0, 0]
    assert projection((2, 3), (0, 0), (4, 0)) == (2.0, 0.0)
    assert reflection((2, 3), (0, 0), (4, 0)) == (2.0, -3.0)
    assert distance_to_line((2, 3), (0, 0), (4, 0)) == 3
    assert line_intersection((0, 0), (2, 2), (0, 2), (2, 0)) == (1.0, 1.0)


def test_minimum_cost_cycle_random():
    rng = random.Random(421307)
    infinity = float("inf")
    for n in range(1, 8):
        for _ in range(300):
            edges = []
            distance = [[infinity] * n for _ in range(n)]
            for vertex in range(n):
                distance[vertex][vertex] = 0
            for first in range(n):
                for second in range(n):
                    if rng.randrange(4) == 0:
                        weight = rng.randrange(10)
                        edges.append((first, second, weight))
                        distance[first][second] = min(distance[first][second], weight)
            for middle in range(n):
                for first in range(n):
                    for second in range(n):
                        distance[first][second] = min(
                            distance[first][second],
                            distance[first][middle] + distance[middle][second],
                        )
            expected = min(
                (weight + distance[second][first] for first, second, weight in edges),
                default=infinity,
            )
            result = minimum_cost_cycle(n, edges)
            assert (result is None) == (expected == infinity)
            if result is not None:
                cost, vertices, edge_ids = result
                assert cost == expected
                assert len(vertices) == len(edge_ids) + 1
                assert vertices[0] == vertices[-1]
                assert sum(edges[edge_id][2] for edge_id in edge_ids) == cost
                for first, second, edge_id in zip(vertices, vertices[1:], edge_ids):
                    assert edges[edge_id][:2] == (first, second)
