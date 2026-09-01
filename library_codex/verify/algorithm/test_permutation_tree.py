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
    root = tree.root
    assert (tree.left[root], tree.right[root]) == (0, len(permutation))
    assert (tree.minimum[root], tree.maximum[root]) == (0, len(permutation) - 1)
    assert tree.parent[root] == -1
    assert tree.node_count <= 2 * len(permutation) - 1

    for index in range(tree.node_count):
        left = tree.left[index]
        right = tree.right[index]
        values = permutation[left:right]
        assert min(values) == tree.minimum[index]
        assert max(values) == tree.maximum[index]
        assert tree.maximum[index] - tree.minimum[index] + 1 == right - left
        children = tree.children(index)
        if tree.kind[index] == tree.LEAF:
            assert right - left == 1
            assert children == []
            continue
        assert len(children) >= 2
        child_left = left
        for child in children:
            assert tree.parent[child] == index
            assert tree.left[child] == child_left
            child_left = tree.right[child]
        assert child_left == right
        if tree.kind[index] == tree.LINEAR_ASC:
            for first, second in zip(children, children[1:]):
                assert tree.maximum[first] + 1 == tree.minimum[second]
        elif tree.kind[index] == tree.LINEAR_DESC:
            for first, second in zip(children, children[1:]):
                assert tree.maximum[second] + 1 == tree.minimum[first]
        else:
            assert tree.kind[index] == tree.PRIME


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
            assert set(zip(tree.left, tree.right)) == brute_strong_intervals(permutation)
            assert_tree_structure(permutation, tree)


def test_permutation_tree_known_kinds_and_debug_output():
    increasing = PermutationTree([0, 1, 2, 3])
    assert increasing.kind[increasing.root] == increasing.LINEAR_ASC
    assert [
        increasing.left[child]
        for child in increasing.children(increasing.root)
    ] == [0, 1, 2, 3]
    assert increasing.count_intervals() == 10

    decreasing = PermutationTree([3, 2, 1, 0])
    assert decreasing.kind[decreasing.root] == decreasing.LINEAR_DESC
    assert decreasing.count_intervals() == 10

    tree = PermutationTree([1, 3, 0, 2])
    assert tree.kind[tree.root] == tree.PRIME
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
    assert tree.children(tree.root) == [0, 1, 2, 3]


def test_permutation_tree_uses_flat_node_arrays():
    tree = PermutationTree([1, 3, 0, 2])
    assert not hasattr(tree, "nodes")
    assert isinstance(tree.kind, bytearray)
    assert tree.kind[tree.root] == tree.PRIME == 3
    assert tree.right[-1] == 4
    assert tree.left[:2] == [0, 1]

    children = tree.children(tree.root)
    children.clear()
    assert tree.children(tree.root) == [0, 1, 2, 3]


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
    assert tree.node_count == 20001
    assert tree.count_intervals() == 20000 * 20001 // 2
