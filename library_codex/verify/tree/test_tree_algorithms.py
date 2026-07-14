from collections import deque
import random

from library_codex.tree.CentroidDecomposition import (
    CentroidDecomposition,
    CentroidDistanceFenwick,
)
from library_codex.tree.DSUOnTree import DSUOnTree
from library_codex.tree.DynamicDiameter import DynamicDiameter
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition
from library_codex.tree.Rerooting import Rerooting
from library_codex.tree.TreeAlgorithms import (
    AuxiliaryTree,
    EulerTour,
    cartesian_tree,
    inclusion_tree,
    inverse_tree,
    process_of_merging_tree,
    rooted_tree,
    tree_diameter,
)


def random_tree(size, rng, weighted=False):
    graph = [[] for _ in range(size)]
    for node in range(1, size):
        parent = rng.randrange(node)
        weight = rng.randrange(1, 21)
        if weighted:
            graph[node].append((parent, weight))
            graph[parent].append((node, weight))
        else:
            graph[node].append(parent)
            graph[parent].append(node)
    return graph


def distances(tree, start):
    result = [-1] * len(tree)
    result[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for entry in tree[node]:
            if isinstance(entry, int):
                other, weight = entry, 1
            else:
                other, weight = entry
            if result[other] < 0:
                result[other] = result[node] + weight
                queue.append(other)
    return result


def test_euler_tour_random_lca_and_forest():
    rng = random.Random(615923)
    for size in range(1, 150):
        tree = random_tree(size, rng)
        root = rng.randrange(size)
        euler = EulerTour(tree, root)
        hld = HeavyLightDecomposition(tree, root)
        assert len(euler) == size * 2 - 1
        for node in range(size):
            left, right = euler.subtree_interval(node)
            assert left < right
            assert euler.tour[left] == node
        for _ in range(100):
            first = rng.randrange(size)
            second = rng.randrange(size)
            assert euler.lca(first, second) == hld.lca(first, second)
            assert euler.distance(first, second) == hld.dist(first, second)

    forest = [[1], [0], [3], [2], []]
    euler = EulerTour(forest, 2)
    assert euler.lca(2, 3) == 2
    assert euler.lca(0, 3) == -1
    assert euler.lca(4, 4) == 4


def test_auxiliary_tree_contains_lcas_and_distances():
    rng = random.Random(172890)
    for size in range(2, 100):
        tree = random_tree(size, rng)
        hld = HeavyLightDecomposition(tree)
        builder = AuxiliaryTree(tree)
        selected = [rng.randrange(size) for _ in range(20)]
        auxiliary, vertices = builder.get(selected, True)
        assert set(selected) <= set(vertices)
        assert sum(map(len, auxiliary)) == len(vertices) - 1
        for parent, row in enumerate(auxiliary):
            for child, distance in row:
                assert hld.lca(vertices[parent], vertices[child]) == vertices[parent]
                assert distance == hld.dist(vertices[parent], vertices[child])
        ordered = sorted(set(selected), key=hld.tin.__getitem__)
        for index in range(len(ordered) - 1):
            assert hld.lca(ordered[index], ordered[index + 1]) in vertices


def test_cartesian_tree_heap_and_inorder():
    rng = random.Random(73156)
    for size in range(101):
        values = [rng.randrange(10) for _ in range(size)]
        parent, left, right, root = cartesian_tree(values)
        if size == 0:
            assert root == -1
            continue
        assert parent[root] == -1
        for node in range(size):
            if left[node] >= 0:
                assert parent[left[node]] == node
                assert values[node] <= values[left[node]]
            if right[node] >= 0:
                assert parent[right[node]] == node
                assert values[node] <= values[right[node]]
        order = []
        stack = []
        node = root
        while stack or node >= 0:
            while node >= 0:
                stack.append(node)
                node = left[node]
            node = stack.pop()
            order.append(node)
            node = right[node]
        assert order == list(range(size))


def test_weighted_tree_diameter_against_all_pairs():
    rng = random.Random(290174)
    for size in range(1, 100):
        tree = random_tree(size, rng, True)
        expected = max(max(distances(tree, node)) for node in range(size))
        distance, path = tree_diameter(tree)
        assert distance == expected
        actual = 0
        for first, second in zip(path, path[1:]):
            actual += next(weight for other, weight in tree[first] if other == second)
        assert actual == distance


def test_hld_tree_query_compatibility():
    tree = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
    hld = HeavyLightDecomposition(tree)
    assert hld.next_on_path(3, 5) == 1
    assert hld.next_on_path(0, 0) == -1
    assert hld.vertices_on_path(3, 5) == [3, 1, 0, 2, 5]


def test_rerooting_weighted_sum_of_distances():
    rng = random.Random(815203)
    for size in range(1, 100):
        tree = random_tree(size, rng, True)
        solver = Rerooting(
            tree,
            lambda first, second: (
                first[0] + second[0], first[1] + second[1]
            ),
            (0, 0),
            lambda value, source, target, weight: (
                value[0], value[1] + value[0] * weight
            ),
            lambda value, vertex: (value[0] + 1, value[1]),
            rng.randrange(size),
        )
        for node in range(size):
            assert solver[node] == (size, sum(distances(tree, node)))


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


def test_tree_algorithms_deep_paths_without_recursion():
    size = 30000
    tree = [[] for _ in range(size)]
    weighted = [[] for _ in range(size)]
    for node in range(size - 1):
        tree[node].append(node + 1)
        tree[node + 1].append(node)
        weighted[node].append((node + 1, 1))
        weighted[node + 1].append((node, 1))
    assert EulerTour(tree).lca(size // 2, size - 1) == size // 2
    assert tree_diameter(tree)[0] == size - 1
    solver = Rerooting(
        weighted,
        lambda first, second: first + second,
        0,
        lambda value, source, target, weight: value,
        lambda value, vertex: value + 1,
    )
    assert solver[0] == solver[size - 1] == size
    decomposition = CentroidDecomposition(tree)
    assert max(decomposition.depth) <= size.bit_length()


def test_rooted_inverse_merging_and_inclusion_trees():
    tree = [[1, 2], [0, 3], [0], [1]]
    directed = rooted_tree(tree, 1)
    assert directed == [
        [2],
        [0, 3],
        [],
        [],
    ]
    assert inverse_tree(directed) == [
        [1],
        [],
        [0],
        [1],
    ]

    graph, weights, root = process_of_merging_tree(
        [(0, 1, 2), (2, 3, 3), (1, 2, 5)], 4
    )
    assert root == 6
    assert weights == [2, 3, 5]
    leaves = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node < 4:
            leaves.append(node)
        else:
            stack.extend(child for child, _ in graph[node])
    assert sorted(leaves) == [0, 1, 2, 3]

    graph, ordered, original = inclusion_tree(
        [(0, 10), (1, 3), (3, 8), (4, 6), (11, 12)], 12
    )
    assert ordered[0] == (-1, 13)
    assert sorted(index for index in original[1:]) == list(range(5))
    assert sum(map(len, graph)) == 5


def test_dsu_on_tree_subtree_distinct_colors():
    rng = random.Random(271605)
    for size in range(1, 100):
        tree = random_tree(size, rng)
        colors = [rng.randrange(15) for _ in range(size)]
        root = rng.randrange(size)
        solver = DSUOnTree(tree, root)
        count = [0] * 15
        distinct = [0]
        answer = [0] * size

        def add(vertex):
            color = colors[vertex]
            if count[color] == 0:
                distinct[0] += 1
            count[color] += 1

        def remove(vertex):
            color = colors[vertex]
            count[color] -= 1
            if count[color] == 0:
                distinct[0] -= 1

        def query(vertex):
            answer[vertex] = distinct[0]

        solver.run(add, query, remove)
        for vertex in range(size):
            subtree = solver.euler[solver.down[vertex] : solver.up[vertex]]
            assert answer[vertex] == len({colors[node] for node in subtree})


def test_dynamic_diameter_random_edge_updates():
    rng = random.Random(751204)
    for size in range(1, 50):
        tree = random_tree(size, rng, True)
        solver = DynamicDiameter(tree)
        expected = tree_diameter(tree)[0]
        assert solver.get()[0] == expected
        if size == 1:
            continue
        edges = [
            (node, other)
            for node in range(size)
            for other, _ in tree[node]
            if node < other
        ]
        for _ in range(100):
            first, second = rng.choice(edges)
            weight = rng.randrange(21)
            for index, (other, _) in enumerate(tree[first]):
                if other == second:
                    tree[first][index] = (other, weight)
                    break
            for index, (other, _) in enumerate(tree[second]):
                if other == first:
                    tree[second][index] = (other, weight)
                    break
            solver.update(first, second, weight)
            assert solver.get()[0] == tree_diameter(tree)[0]
