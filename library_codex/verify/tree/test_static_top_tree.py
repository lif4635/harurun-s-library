import random

from library_codex.tree.StaticTopTree import (
    DynamicRerootingDP,
    DynamicTreeDP,
    EdgeTopTreeDP,
    StaticTopTree,
    StaticTopTreeVertexBased,
    VertexTopTreeDP,
)


def random_tree(size, rng):
    graph = [[] for _ in range(size)]
    for node in range(1, size):
        parent = rng.randrange(node)
        graph[node].append(parent)
        graph[parent].append(node)
    return graph


def validate_cluster_tree(tree):
    seen = bytearray(len(tree.parent))
    stack = [tree.top_tree_root]
    while stack:
        node = stack.pop()
        assert not seen[node]
        seen[node] = 1
        left = tree.left[node]
        right = tree.right[node]
        if left >= 0:
            assert tree.parent[left] == node
            stack.append(left)
        if right >= 0:
            assert tree.parent[right] == node
            stack.append(right)
    assert all(seen)
    assert tree.parent[tree.top_tree_root] == -1


def test_static_top_tree_structure_and_incremental_builder():
    rng = random.Random(826413)
    for size in range(1, 100):
        graph = random_tree(size, rng)
        root = rng.randrange(size)
        tree = StaticTopTree(graph, root)
        assert len(tree.parent) == size * 2 - 1
        assert tree.height() <= 4 * size.bit_length() + 1
        validate_cluster_tree(tree)

        edges = [
            (node, other)
            for node in range(size)
            for other in graph[node]
            if node < other
        ]
        incremental = StaticTopTree(size, root)
        for first, second in edges:
            incremental.add_edge(first, second)
        incremental.run()
        assert len(incremental.parent) == size * 2 - 1
        validate_cluster_tree(incremental)


def test_dynamic_tree_dp_point_updates():
    rng = random.Random(930571)
    for size in range(1, 80):
        graph = random_tree(size, rng)
        values = [rng.randrange(-100, 101) for _ in range(size)]
        top_tree = StaticTopTree(graph, rng.randrange(size))
        solver = DynamicTreeDP(
            top_tree,
            values.__getitem__,
            lambda left, right: left + right,
            lambda upper, lower: upper + lower,
        )
        assert solver.get() == sum(values)
        for _ in range(100):
            node = rng.randrange(size)
            value = rng.randrange(-100, 101)
            values[node] = value
            solver.set(node, value)
            assert solver.get() == sum(values)


def test_edge_top_tree_dp_external_values():
    rng = random.Random(149205)
    size = 100
    graph = random_tree(size, rng)
    root = 37
    top_tree = StaticTopTree(graph, root)
    values = [rng.randrange(-50, 51) for _ in range(size)]
    values[root] = 0
    solver = EdgeTopTreeDP(
        top_tree,
        values.__getitem__,
        lambda left, right: left + right,
        lambda first, second: first + second,
    )
    assert solver.get() == sum(values)
    for _ in range(3000):
        node = rng.randrange(size)
        if node == root:
            continue
        values[node] = rng.randrange(-50, 51)
        solver.update(node)
        assert solver.get() == sum(values)


def test_dynamic_rerooting_dp_additive_invariant():
    rng = random.Random(79135)
    size = 120
    graph = random_tree(size, rng)
    root = 19
    top_tree = StaticTopTree(graph, root)
    values = [rng.randrange(-30, 31) for _ in range(size)]
    values[root] = 0
    solver = DynamicRerootingDP(
        top_tree,
        lambda node: (values[node], values[node]),
        lambda first, second: first + second,
        lambda first, second: first + second,
        lambda first, second: first + second,
        lambda: 0,
    )
    expected = sum(values)
    assert all(solver.get(node) == expected for node in range(size))
    for _ in range(500):
        node = rng.randrange(size)
        if node == root:
            continue
        values[node] = rng.randrange(-30, 31)
        solver.set(node, (values[node], values[node]))
        expected = sum(values)
        for _ in range(5):
            assert solver.get(rng.randrange(size)) == expected


def test_vertex_based_static_top_tree_dp():
    rng = random.Random(521907)
    for size in range(1, 100):
        graph = random_tree(size, rng)
        values = [rng.randrange(-100, 101) for _ in range(size)]
        top_tree = StaticTopTreeVertexBased(graph, rng.randrange(size))
        validate_cluster_tree(top_tree)
        assert top_tree.height() <= 6 * size.bit_length() + 1
        solver = VertexTopTreeDP(
            top_tree,
            values.__getitem__,
            lambda first, second: first + second,
            lambda first, second: first + second,
            lambda path: path,
            lambda point, node: point + values[node],
        )
        assert solver.get() == sum(values)
        for _ in range(100):
            node = rng.randrange(size)
            values[node] = rng.randrange(-100, 101)
            solver.update(node)
            assert solver.get() == sum(values)


def test_static_top_tree_deep_path_without_recursion():
    size = 100000
    graph = [[] for _ in range(size)]
    for node in range(size - 1):
        graph[node].append(node + 1)
        graph[node + 1].append(node)
    tree = StaticTopTree(graph)
    assert len(tree.parent) == size * 2 - 1
    assert tree.height() <= size.bit_length() + 1
    solver = DynamicTreeDP(
        tree,
        lambda node: node,
        lambda first, second: first + second,
        lambda first, second: first + second,
    )
    assert solver.get() == size * (size - 1) // 2
