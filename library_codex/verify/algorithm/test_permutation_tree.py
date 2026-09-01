import itertools
import random

import pytest

from library_codex.algorithm.PermutationTree import PermutationTree


def brute_intervals(permutation):
    result = set()
    for left in range(len(permutation)):
        minimum = maximum = permutation[left]
        for right in range(left + 1, len(permutation) + 1):
            value = permutation[right - 1]
            minimum = min(minimum, value)
            maximum = max(maximum, value)
            if maximum - minimum == right - left - 1:
                result.add((left, right))
    return result


def brute_strong_intervals(permutation):
    intervals = brute_intervals(permutation)
    result = set()
    for left, right in intervals:
        if all(
            other_right <= left
            or right <= other_left
            or (left <= other_left and other_right <= right)
            or (other_left <= left and right <= other_right)
            for other_left, other_right in intervals
        ):
            result.add((left, right))
    return result


def assert_tree_structure(permutation, tree):
    nodes = tree.nodes
    root = nodes[tree.root]
    assert (root.left, root.right) == (0, len(permutation))
    assert (root.minimum, root.maximum) == (0, len(permutation) - 1)
    assert root.parent == -1
    assert len(nodes) <= 2 * len(permutation) - 1

    for index, node in enumerate(nodes):
        values = permutation[node.left:node.right]
        assert min(values) == node.minimum
        assert max(values) == node.maximum
        assert node.maximum - node.minimum + 1 == node.size
        if node.kind == tree.LEAF:
            assert node.size == 1
            assert node.children == []
            continue
        assert len(node.children) >= 2
        left = node.left
        for child_index in node.children:
            child = nodes[child_index]
            assert child.parent == index
            assert child.left == left
            left = child.right
        assert left == node.right
        if node.kind == tree.LINEAR_ASC:
            for first, second in zip(node.children, node.children[1:]):
                assert nodes[first].maximum + 1 == nodes[second].minimum
        elif node.kind == tree.LINEAR_DESC:
            for first, second in zip(node.children, node.children[1:]):
                assert nodes[second].maximum + 1 == nodes[first].minimum
        else:
            assert node.kind == tree.PRIME


def test_permutation_tree_against_brute_force():
    rng = random.Random(4635)
    for n in range(1, 10):
        cases = list(itertools.permutations(range(n))) if n <= 5 else []
        for _ in range(300):
            permutation = list(range(n))
            rng.shuffle(permutation)
            cases.append(tuple(permutation))
        for case in cases:
            permutation = list(case)
            tree = PermutationTree(permutation)
            want = brute_intervals(permutation)
            assert set(tree.intervals()) == want
            assert len(tree.intervals()) == len(want)
            assert tree.count_intervals() == len(want)
            assert {
                (node.left, node.right) for node in tree.nodes
            } == brute_strong_intervals(permutation)
            assert_tree_structure(permutation, tree)


def test_permutation_tree_known_kinds_and_debug_output():
    increasing = PermutationTree([0, 1, 2, 3])
    assert increasing.nodes[increasing.root].kind == increasing.LINEAR_ASC
    assert [
        increasing.nodes[child].left
        for child in increasing.nodes[increasing.root].children
    ] == [0, 1, 2, 3]
    assert increasing.count_intervals() == 10

    decreasing = PermutationTree([3, 2, 1, 0])
    assert decreasing.nodes[decreasing.root].kind == decreasing.LINEAR_DESC
    assert decreasing.count_intervals() == 10

    tree = PermutationTree([1, 3, 0, 2])
    assert tree.nodes[tree.root].kind == tree.PRIME
    rows = tree.tolist()
    assert rows[tree.root] == {
        "kind": "prime",
        "left": 0,
        "right": 4,
        "minimum": 0,
        "maximum": 3,
        "parent": -1,
        "children": [0, 1, 2, 3],
    }
    assert str(tree) == str(rows)
    assert repr(tree) == "PermutationTree(%r)" % rows
    rows[tree.root]["children"].clear()
    assert tree.nodes[tree.root].children == [0, 1, 2, 3]


def test_permutation_tree_nodes_are_lazy_read_only_views():
    tree = PermutationTree([1, 3, 0, 2])
    first = tree.nodes[tree.root]
    second = tree.nodes[tree.root]

    assert first is not second
    assert first.kind == second.kind == tree.PRIME
    assert tree.nodes[-1].right == 4
    assert [node.left for node in tree.nodes[:2]] == [0, 1]

    children = first.children
    children.clear()
    assert second.children == [0, 1, 2, 3]
    with pytest.raises(AttributeError):
        first.left = 10


def test_permutation_tree_rejects_invalid_input():
    with pytest.raises(ValueError, match="nonempty"):
        PermutationTree([])
    with pytest.raises(ValueError, match=r"range\(n\)"):
        PermutationTree([0, 0])
    with pytest.raises(ValueError, match=r"range\(n\)"):
        PermutationTree([1])


def test_permutation_tree_large_input_is_iterative():
    permutation = list(range(20000))
    tree = PermutationTree(permutation)
    assert len(tree.nodes) == 20001
    assert tree.count_intervals() == 20000 * 20001 // 2
