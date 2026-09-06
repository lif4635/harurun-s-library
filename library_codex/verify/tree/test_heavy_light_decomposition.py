import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.tree.HeavyLightDecomposition import HLD


def make_path(parent, depth, u, v):
    left = []
    right = []
    while depth[u] > depth[v]:
        left.append(u)
        u = parent[u]
    while depth[v] > depth[u]:
        right.append(v)
        v = parent[v]
    while u != v:
        left.append(u)
        right.append(v)
        u = parent[u]
        v = parent[v]
    left.append(u)
    return left + right[::-1]


def restore(hld, segments):
    res = []
    for l, r, reverse in segments:
        part = hld.rev[l:r]
        if reverse:
            part.reverse()
        res.extend(part)
    return res


def test_random():
    for n in range(1, 100):
        edge = [[] for _ in range(n)]
        for v in range(1, n):
            p = random.randrange(v)
            edge[p].append(v)
            edge[v].append(p)

        root = random.randrange(n)
        parent = [-1] * n
        depth = [0] * n
        order = [root]
        for u in order:
            for v in edge[u]:
                if v != parent[u]:
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    order.append(v)

        hld = HLD(edge, root)
        assert hld.parent == parent
        assert sorted(hld.rev) == list(range(n))

        for v in range(n):
            l, r = hld.subtree(v)
            got = set(hld.rev[l:r])
            want = {u for u in range(n) if v in make_path(parent, depth, root, u)}
            assert got == want

        for _ in range(300):
            u = random.randrange(n)
            v = random.randrange(n)
            path = make_path(parent, depth, u, v)
            w = min(path, key=depth.__getitem__)
            assert hld.lca(u, v) == w
            assert hld.dist(u, v) == len(path) - 1
            assert restore(hld, hld.path_ordered(u, v)) == path

            edge_path = [x for x in path if x != w]
            assert restore(hld, hld.path_ordered(u, v, True)) == edge_path
            got = []
            for l, r in hld.path(u, v, True):
                got.extend(hld.rev[l:r])
            assert sorted(got) == sorted(edge_path)

            for k, x in enumerate(path):
                assert hld.jump(u, v, k) == x
            assert hld.jump(u, v, len(path)) == -1

        for v in range(n):
            x = v
            for k in range(depth[v] + 1):
                assert hld.kth_ancestor(v, k) == x
                x = parent[x]
            assert hld.kth_ancestor(v, depth[v] + 1) == -1


def test_long_path_without_recursion():
    n = 100000
    edge = [[] for _ in range(n)]
    for v in range(1, n):
        edge[v - 1].append(v)
        edge[v].append(v - 1)
    hld = HLD(edge)
    assert hld.lca(n - 1, n // 2) == n // 2
    assert hld.jump(n - 1, 0, n - 1) == 0
    assert hld.subtree(n // 2) == (n // 2, n)


def test_documented_subtree_and_direction_examples():
    from library_codex.segment_tree.LazySegTree import LazySegTree

    hld = HLD([[1, 2], [0, 3, 4], [0], [1], [1]])
    values = [10, 20, 30, 40, 50]
    ordered = [values[v] for v in hld.rev]
    assert ordered == [10, 20, 40, 50, 30]
    assert hld.subtree(1) == (1, 4)
    assert hld.subtree(1, edge=True) == (2, 4)
    assert hld.path_ordered(3, 2) == [(0, 3, True), (4, 5, False)]
    assert restore(hld, hld.path_ordered(3, 2)) == [3, 1, 0, 2]
    seg = LazySegTree(
        lambda a, b: a + b, 0,
        lambda delta, value, length: value + delta * length,
        lambda new, old: new + old, 0, ordered,
    )
    l, r = hld.subtree(1)
    seg.apply(l, r, 5)
    assert [seg.get(hld.index(v)) for v in range(5)] == [10, 25, 30, 45, 55]
    for l, r, reverse in hld.path_ordered(3, 2, edge=True):
        vertices = hld.rev[l:r]
        if reverse:
            vertices.reverse()
        for v in vertices:
            start, end = (v, hld.parent[v]) if reverse else (hld.parent[v], v)
            assert (start, end) in [(3, 1), (1, 0), (0, 2)]
    assert hld.path_ordered(1, 1, edge=True) == []
    l, r = hld.subtree(3, edge=True)
    assert l == r


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_long_path_without_recursion()
