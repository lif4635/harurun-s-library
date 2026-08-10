from collections import deque
from random import Random

from library_codex.tree_query.TreeWaveletMatrix import TreeWaveletMatrix


def _parent_depth(tree, root):
    parent = [-1] * len(tree)
    depth = [0] * len(tree)
    order = [root]
    for vertex in order:
        for to in tree[vertex]:
            if to != parent[vertex]:
                parent[to] = vertex
                depth[to] = depth[vertex] + 1
                order.append(to)
    return parent, depth, order


def _path(parent, depth, first, second):
    left = []
    right = []
    while depth[first] > depth[second]:
        left.append(first)
        first = parent[first]
    while depth[second] > depth[first]:
        right.append(second)
        second = parent[second]
    while first != second:
        left.append(first)
        right.append(second)
        first = parent[first]
        second = parent[second]
    left.append(first)
    return left + right[::-1]


def test_tree_wavelet_matrix_matches_bruteforce():
    rng = Random(5201)
    for n in range(1, 32):
        for _ in range(18):
            tree = [[] for _ in range(n)]
            for vertex in range(1, n):
                parent = rng.randrange(vertex)
                tree[parent].append(vertex)
                tree[vertex].append(parent)
            values = [rng.randrange(-10, 11) for _ in range(n)]
            root = rng.randrange(n)
            structure = TreeWaveletMatrix(tree, values, root)
            parent, depth, order = _parent_depth(tree, root)
            descendants = [[vertex] for vertex in range(n)]
            for vertex in reversed(order[1:]):
                descendants[parent[vertex]].extend(descendants[vertex])

            for _query in range(40):
                first = rng.randrange(n)
                second = rng.randrange(n)
                path_values = sorted(values[v] for v in _path(
                    parent, depth, first, second
                ))
                k = rng.randrange(len(path_values))
                assert structure.kth_path(first, second, k) == path_values[k]
                lower = rng.randrange(-12, 13)
                upper = rng.randrange(lower, 14)
                assert structure.count_path(first, second, lower, upper) == sum(
                    lower <= value < upper for value in path_values
                )

                vertex = rng.randrange(n)
                subtree_values = sorted(values[v] for v in descendants[vertex])
                k = rng.randrange(len(subtree_values))
                assert structure.kth_subtree(vertex, k) == subtree_values[k]
                assert structure.count_subtree(vertex, lower, upper) == sum(
                    lower <= value < upper for value in subtree_values
                )

            assert structure.tolist() == values
            assert str(structure) == str(values)
            assert repr(structure) == "TreeWaveletMatrix(%r)" % values


def test_tree_wavelet_matrix_handles_a_deep_tree_without_recursion():
    n = 20000
    tree = [[] for _ in range(n)]
    for vertex in range(1, n):
        tree[vertex - 1].append(vertex)
        tree[vertex].append(vertex - 1)
    structure = TreeWaveletMatrix(tree, list(range(n)))
    assert structure.kth_path(0, n - 1, n - 1) == n - 1
    assert structure.count_subtree(0, 123, 456) == 333
