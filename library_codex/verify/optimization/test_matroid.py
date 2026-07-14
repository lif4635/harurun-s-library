import itertools
import random

from library_codex.optimization.Matroid import (
    GraphicMatroid,
    PartitionMatroid,
    TransversalMatroid,
    minimum_matroid_intersection,
)


def _graphic_independent(vertex_count, edges, mask):
    parent = list(range(vertex_count))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge, (first, second) in enumerate(edges):
        if mask >> edge & 1:
            first = find(first)
            second = find(second)
            if first == second:
                return False
            parent[second] = first
    return True


def _partition_independent(groups, limits, mask):
    count = [0] * len(limits)
    for element, group in enumerate(groups):
        if mask >> element & 1 and group >= 0:
            count[group] += 1
    return all(count[group] <= limits[group] for group in range(len(limits)))


def _transversal_independent(graph, right_size, mask):
    selected = [left for left in range(len(graph)) if mask >> left & 1]
    for targets in itertools.permutations(range(right_size), len(selected)):
        if all(target in graph[left] for left, target in zip(selected, targets)):
            return True
    return not selected


def _expected(weights, first_predicate, second_predicate):
    size = len(weights)
    answer = {}
    for mask in range(1 << size):
        if first_predicate(mask) and second_predicate(mask):
            cardinality = mask.bit_count()
            value = sum(weights[index] for index in range(size) if mask >> index & 1)
            answer[cardinality] = min(answer.get(cardinality, 10 ** 30), value)
    return [answer[index] for index in range(max(answer) + 1)]


def test_graphic_partition_matroid_intersection_against_subsets():
    rng = random.Random(72)
    for _ in range(300):
        vertices = rng.randrange(1, 6)
        size = rng.randrange(1, 11)
        edges = [(rng.randrange(vertices), rng.randrange(vertices)) for _ in range(size)]
        groups = [rng.randrange(3) for _ in range(size)]
        limits = [rng.randrange(4) for _ in range(3)]
        weights = [rng.randrange(-20, 21) for _ in range(size)]
        costs, selections = minimum_matroid_intersection(
            GraphicMatroid(vertices, edges), PartitionMatroid(groups, limits), weights
        )
        expected = _expected(
            weights,
            lambda mask: _graphic_independent(vertices, edges, mask),
            lambda mask: _partition_independent(groups, limits, mask),
        )
        assert costs == expected
        for cardinality, selected in enumerate(selections):
            assert sum(selected) == cardinality
            assert sum(weight for weight, chosen in zip(weights, selected) if chosen) == costs[cardinality]


def test_partition_transversal_matroid_intersection_against_subsets():
    rng = random.Random(73)
    for _ in range(200):
        size = rng.randrange(1, 9)
        right_size = rng.randrange(1, 6)
        graph = [[right for right in range(right_size) if rng.randrange(2)]
                 for _ in range(size)]
        edges = [(left, right) for left, row in enumerate(graph) for right in row]
        groups = [rng.randrange(2) for _ in range(size)]
        limits = [rng.randrange(4) for _ in range(2)]
        weights = [rng.randrange(-15, 16) for _ in range(size)]
        costs, _ = minimum_matroid_intersection(
            PartitionMatroid(groups, limits),
            TransversalMatroid(size, right_size, edges),
            weights,
        )
        expected = _expected(
            weights,
            lambda mask: _partition_independent(groups, limits, mask),
            lambda mask: _transversal_independent(graph, right_size, mask),
        )
        assert costs == expected
