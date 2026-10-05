import random

import pytest

from library_codex.tree.CentroidDecomposition import CentroidDecomposition, CentroidDistanceFenwick


def random_tree(size, rng):
    graph = [[] for _ in range(size)]
    for node in range(1, size):
        parent = rng.randrange(node)
        graph[node].append(parent)
        graph[parent].append(node)
    return graph


def distances(tree, start):
    result = [-1] * len(tree)
    result[start] = 0
    queue = [start]
    for node in queue:
        for other in tree[node]:
            if result[other] < 0:
                result[other] = result[node] + 1
                queue.append(other)
    return result


def test_centroid_decomposition_paths_and_distance_fenwick():
    rng = random.Random(480216)
    for size in range(1, 80):
        tree = random_tree(size, rng)
        decomposition = CentroidDecomposition(tree)
        assert decomposition.parent[decomposition.root] == -1
        assert len(decomposition.order) == size
        all_distance = [distances(tree, node) for node in range(size)]
        for vertex in range(size):
            path = decomposition.paths[vertex]
            assert path[-1][0] == vertex
            for centroid, distance, _ in path:
                assert distance == all_distance[vertex][centroid]
            for first, second in zip(path, path[1:]):
                assert decomposition.parent[second[0]] == first[0]

        values = [rng.randrange(-20, 21) for _ in range(size)]
        solver = CentroidDistanceFenwick(tree, values)
        for _ in range(300):
            if rng.randrange(3) == 0:
                vertex = rng.randrange(size)
                value = rng.randrange(-20, 21)
                values[vertex] = value
                solver.set(vertex, value)
            else:
                vertex = rng.randrange(size)
                lower = rng.randrange(size + 1)
                upper = rng.randrange(lower, size + 2)
                expected = sum(
                    values[node]
                    for node in range(size)
                    if lower <= all_distance[vertex][node] < upper
                )
                assert solver.query(vertex, lower, upper) == expected


def test_deep_path_and_debug_output():
    n = 30000
    tree = [[] for _ in range(n)]
    for node in range(1, n):
        tree[node].append(node - 1)
        tree[node - 1].append(node)
    solver = CentroidDistanceFenwick(tree, range(n))
    assert max(solver.decomposition.depth) <= n.bit_length()
    assert solver.query(0, 0, n) == n * (n - 1) // 2
    assert solver.query(n - 1, 0, 2) == 2 * n - 3
    assert solver.query(n // 2, -10, 0) == 0
    solver.add(n - 1, 7)
    assert solver.query(n - 1, 0, 1) == n + 6
    values = list(range(n))
    values[-1] += 7
    assert solver.tolist() == values
    assert str(solver) == str(values)
    assert repr(solver) == "CentroidDistanceFenwick(%r)" % values
    copy = solver.tolist()
    copy[0] = -99
    assert solver.query(0, 0, 1) == 0


def test_singleton_initial_values_and_empty_ranges():
    solver = CentroidDistanceFenwick([[]], [10**30])
    assert solver.query(0) == 10**30
    for left, right in ((0, 0), (3, 2), (1, 9), (-5, 0)):
        assert solver.query(0, left, right) == 0
    solver.set(0, -10**30)
    assert solver.query(0, -1, 1) == -10**30
    with pytest.raises(ValueError):
        CentroidDistanceFenwick([[]], [])


def test_fractional_and_infinite_distance_bounds():
    from decimal import Decimal
    from fractions import Fraction

    graph = [[1], [0, 2], [1, 3], [2]]
    values = [2, 3, 5, 7]
    solver = CentroidDistanceFenwick(graph, values)
    bounds = [-float("inf"), -0.5, 0, 0.5, Fraction(3, 2), Decimal("2.1"), 3, 4.5, float("inf")]
    for vertex in range(4):
        for lower in bounds:
            for upper in bounds:
                expected = sum(value for other, value in enumerate(values) if lower <= abs(other - vertex) < upper)
                assert solver.query(vertex, lower, upper) == expected
