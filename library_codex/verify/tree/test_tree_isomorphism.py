import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.tree.PruferCode import prufer_decode
from library_codex.tree.TreeIsomorphism import (
    AHUInterner,
    RootedTreeHash,
    RootedTreeIsomorphism,
    rooted_tree_isomorphic,
    rooted_tree_hashes,
    tree_center,
    tree_centroid,
    tree_hash,
    unrooted_tree_isomorphic,
)


def relabel(tree, permutation):
    n = len(tree)
    result = [[] for _ in range(n)]
    for u in range(n):
        for v in tree[u]:
            result[permutation[u]].append(permutation[v])
    return result


def brute_key(tree, root=None):
    n = len(tree)
    if n == 0:
        return ()
    vertices = range(n)
    if root is None:
        permutations = itertools.permutations(vertices)
    else:
        rest = [v for v in vertices if v != root]
        permutations = ((root, *tail) for tail in itertools.permutations(rest))
    best = None
    for permutation in permutations:
        position = [0] * n
        for i, v in enumerate(permutation):
            position[v] = i
        value = 0
        for u in range(n):
            for v in tree[u]:
                if position[u] < position[v]:
                    index = position[v] * (position[v] - 1) // 2 + position[u]
                    value |= 1 << index
        if best is None or value < best:
            best = value
    return best


def test_rooted_subtree_classification():
    rng = random.Random(0)
    for n in range(1, 100):
        code = [rng.randrange(n) for _ in range(max(0, n - 2))]
        tree = prufer_decode(code, n)
        result = RootedTreeIsomorphism(tree)
        forms = [None] * n
        for v in reversed(result.order):
            forms[v] = tuple(sorted(forms[to] for to in tree[v] if result.parent[to] == v))
        for u in range(n):
            for v in range(n):
                assert result.same_subtree(u, v) == (forms[u] == forms[v])
        assert result.num_classes == len(set(forms))
        assert rooted_tree_hashes(tree) == result.hashes
        assert RootedTreeHash is RootedTreeIsomorphism


def test_exact_isomorphism_against_brute():
    rng = random.Random(1)
    samples = []
    for _ in range(100):
        n = rng.randrange(1, 8)
        tree = prufer_decode([rng.randrange(n) for _ in range(max(0, n - 2))], n)
        samples.append((tree, brute_key(tree)))
        permutation = list(range(n))
        rng.shuffle(permutation)
        other = relabel(tree, permutation)
        assert unrooted_tree_isomorphic(tree, other)
        assert tree_hash(tree) == tree_hash(other)
        root = rng.randrange(n)
        assert rooted_tree_isomorphic(tree, root, other, permutation[root])

    for _ in range(500):
        tree1, key1 = rng.choice(samples)
        tree2, key2 = rng.choice(samples)
        expected = len(tree1) == len(tree2) and key1 == key2
        assert unrooted_tree_isomorphic(tree1, tree2) == expected


def test_shared_interner_and_centers():
    path = [[1], [0, 2], [1, 3], [2, 4], [3]]
    star = [[1, 2, 3, 4], [0], [0], [0], [0]]
    assert tree_center(path) == [2]
    assert tree_centroid(path) == [2]
    assert tree_center(star) == [0]
    assert tree_centroid(star) == [0]
    assert not unrooted_tree_isomorphic(path, star)

    interner = AHUInterner()
    first = RootedTreeIsomorphism(path, 2, interner)
    second = RootedTreeIsomorphism(relabel(path, [4, 3, 2, 1, 0]), 2, interner)
    assert first.class_id[2] == second.class_id[2]


def test_deep_tree_without_recursion():
    n = 200000
    tree = [[] for _ in range(n)]
    for v in range(n - 1):
        tree[v].append(v + 1)
        tree[v + 1].append(v)
    result = RootedTreeIsomorphism(tree)
    assert result.height[0] == n - 1
    assert result.num_classes == n
    assert tree_center(tree) == [n // 2 - 1, n // 2]
    assert tree_centroid(tree) == [n // 2 - 1, n // 2]


if __name__ == "__main__":
    test_rooted_subtree_classification()
    test_exact_isomorphism_against_brute()
    test_shared_interner_and_centers()
    test_deep_tree_without_recursion()
