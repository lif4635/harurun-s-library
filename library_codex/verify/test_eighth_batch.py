import itertools
import math
import random

from library_codex.algorithm.Sorting import (
    compose_permutations,
    inverse_permutation,
    permutation_cycles,
    permutation_power,
)
from library_codex.geometry.CircleGeometry import (
    circle_circle_intersections,
    circle_line_intersections,
    tangent_points,
)
from library_codex.geometry.ConvexHull import convex_hull
from library_codex.geometry.ConvexPolygon import ConvexPolygon
from library_codex.geometry.PointInPolygon import point_location
from library_codex.graph_connectivity.FunctionalGraph import FunctionalGraph
from library_codex.graph_matching.BipartiteMatching import BipartiteMatching
from library_codex.range_query.RangeMajority import RangeMajority
from library_codex.range_query.StaticRangeMode import StaticRangeMode
from library_codex.tree.LCA import LCA


def tree_path(tree, source, target):
    parent = [-1] * len(tree)
    parent[source] = source
    queue = [source]
    for vertex in queue:
        if vertex == target:
            break
        for other in tree[vertex]:
            if parent[other] < 0:
                parent[other] = vertex
                queue.append(other)
    result = []
    vertex = target
    while vertex != source:
        result.append(vertex)
        vertex = parent[vertex]
    result.append(source)
    return result[::-1]


def test_range_mode_and_majority_random():
    rng = random.Random(871246)
    for size in range(1, 100):
        values = [rng.randrange(12) for _ in range(size)]
        mode = StaticRangeMode(values)
        majority = RangeMajority(values)
        for _ in range(500):
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            if left == right:
                assert mode.mode(left, right) == (None, 0)
                assert majority.majority(left, right) is None
                continue
            expected_count = max(values[left:right].count(value) for value in set(values[left:right]))
            expected_value = next(
                value for value in values[left:right]
                if values[left:right].count(value) == expected_count
            )
            assert mode.mode(left, right) == (expected_value, expected_count)
            expected_majority = (
                (expected_value, expected_count)
                if expected_count * 2 > right - left else None
            )
            assert majority.majority(left, right) == expected_majority


def test_convex_polygon_against_general_location():
    rng = random.Random(481023)
    for _ in range(500):
        points = {(rng.randrange(-20, 21), rng.randrange(-20, 21)) for _ in range(30)}
        hull = convex_hull(points, keep_collinear=False)
        if len(hull) < 3:
            continue
        solver = ConvexPolygon(hull)
        reverse = ConvexPolygon(list(reversed(hull)))
        for _ in range(100):
            point = (rng.randrange(-25, 26), rng.randrange(-25, 26))
            expected = point_location(hull, point)
            assert solver.location(point) == expected
            assert reverse.location(point) == expected


def test_circle_geometry():
    line = circle_line_intersections((0, 0), 5, (-10, 0), (10, 0))
    assert line == [(-5.0, 0.0), (5.0, 0.0)]
    assert circle_line_intersections((0, 0), 1, (0, 2), (1, 2)) == []
    circles = circle_circle_intersections((0, 0), 5, (8, 0), 5)
    assert len(circles) == 2
    assert all(math.isclose(x, 4) and math.isclose(abs(y), 3) for x, y in circles)
    assert circle_circle_intersections((0, 0), 2, (0, 0), 2) is None
    tangent = tangent_points((0, 0), 1, (2, 0))
    assert len(tangent) == 2
    for x, y in tangent:
        assert math.isclose(x * x + y * y, 1)
        assert math.isclose((x - 2) * x + y * y, 0, abs_tol=1e-12)


def test_permutation_operations_exhaustive():
    for size in range(8):
        for permutation in itertools.permutations(range(size)):
            permutation = list(permutation)
            inverse = inverse_permutation(permutation)
            assert compose_permutations(permutation, inverse) == list(range(size))
            assert compose_permutations(inverse, permutation) == list(range(size))
            covered = sorted(vertex for cycle in permutation_cycles(permutation, True) for vertex in cycle)
            assert covered == list(range(size))
            for exponent in range(-8, 9):
                powered = permutation_power(permutation, exponent)
                for vertex in range(size):
                    current = vertex
                    if exponent >= 0:
                        for _ in range(exponent):
                            current = permutation[current]
                    else:
                        for _ in range(-exponent):
                            current = inverse[current]
                    assert powered[vertex] == current


def test_lca_path_intersection_random():
    rng = random.Random(103875)
    for size in range(1, 80):
        tree = [[] for _ in range(size)]
        for vertex in range(1, size):
            parent = rng.randrange(vertex)
            tree[vertex].append(parent)
            tree[parent].append(vertex)
        solver = LCA(tree)
        for _ in range(1000):
            first, second, third, fourth = [rng.randrange(size) for _ in range(4)]
            path1 = tree_path(tree, first, second)
            path2 = tree_path(tree, third, fourth)
            common = set(path1) & set(path2)
            result = solver.path_intersection(first, second, third, fourth)
            if not common:
                assert result is None
                continue
            assert result is not None
            begin, end = result
            assert set(tree_path(tree, begin, end)) == common
            for vertex in range(size):
                assert solver.on_path(vertex, first, second) == (vertex in path1)


def test_functional_graph_first_meeting_random():
    rng = random.Random(734091)
    for size in range(1, 100):
        to = [rng.randrange(size) for _ in range(size)]
        solver = FunctionalGraph(to)
        for first in range(size):
            for second in range(size):
                expected = -1
                left = first
                right = second
                for time in range(2 * size + 1):
                    if left == right:
                        expected = time
                        break
                    left = to[left]
                    right = to[right]
                assert solver.first_meeting(first, second) == expected
                result = solver.meeting_vertex(first, second)
                if expected < 0:
                    assert result is None
                else:
                    assert result == (expected, solver.move(first, expected))


def all_maximum_matchings(left_size, right_size, edges):
    edges = sorted(set(edges))
    result = []
    best = -1
    for mask in range(1 << len(edges)):
        selected = [edges[index] for index in range(len(edges)) if mask >> index & 1]
        if len({left for left, _ in selected}) != len(selected):
            continue
        if len({right for _, right in selected}) != len(selected):
            continue
        if len(selected) > best:
            best = len(selected)
            result = [set(selected)]
        elif len(selected) == best:
            result.append(set(selected))
    return result


def test_bipartite_allowed_and_essential_edges_exhaustive():
    rng = random.Random(621508)
    for left_size in range(1, 5):
        for right_size in range(1, 5):
            universe = [(left, right) for left in range(left_size) for right in range(right_size)]
            for _ in range(1000):
                edges = [edge for edge in universe if rng.randrange(3) == 0]
                matcher = BipartiteMatching(left_size, right_size)
                for edge in edges:
                    matcher.add_edge(*edge)
                maximum = all_maximum_matchings(left_size, right_size, edges)
                allowed = set().union(*maximum)
                essential = set.intersection(*maximum)
                assert set(matcher.allowed_edges()) == allowed
                assert set(matcher.essential_edges()) == essential
