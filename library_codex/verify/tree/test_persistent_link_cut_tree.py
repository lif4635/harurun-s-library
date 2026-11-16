import random
import pytest
from library_codex.tree.PersistentLinkCutTree import PersistentLinkCutTree


def path(edges, n, u, v):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = {u: -1}
    queue = [u]
    for x in queue:
        for y in adj[x]:
            if y not in parent:
                parent[y] = x
                queue.append(y)
    if v not in parent:
        return None
    answer = []
    while v != -1:
        answer.append(v)
        v = parent[v]
    return answer[::-1]


def test_forest_versions_noncommutative_and_failed_operations():
    rng = random.Random(31624)
    n = 12
    values = list("abcdefghijkl")
    initial = {(0, 1), (1, 2), (3, 4)}
    tree = PersistentLinkCutTree(values, lambda a, b: a + b, "", initial)
    versions = [(initial, values)]
    for _ in range(1400):
        version = rng.randrange(len(versions))
        edges, values = versions[version]
        u, v = rng.randrange(n), rng.randrange(n)
        p = path(edges, n, u, v)
        kind = rng.randrange(7)
        next_edges, next_values = edges, values
        if kind == 0:
            new, ok = tree.link(u, v, version)
            assert ok == (p is None)
            if ok:
                next_edges = edges | {tuple(sorted((u, v)))}
        elif kind == 1:
            new, ok = tree.cut(u, v, version)
            edge = tuple(sorted((u, v)))
            assert ok == (edge in edges)
            if ok:
                next_edges = edges - {edge}
        elif kind == 2:
            next_values = values.copy()
            next_values[u] = chr(65 + rng.randrange(26))
            new = tree.set(u, next_values[u], version)
        elif kind == 3:
            new, same = tree.same(u, v, version)
            assert same == (p is not None)
        elif p is None:
            with pytest.raises(ValueError):
                tree.prod(u, v, version)
            continue
        elif kind == 4:
            new, product = tree.prod(u, v, version)
            assert product == "".join(values[x] for x in p)
        elif kind == 5:
            new, size = tree.path_size(u, v, version)
            assert size == len(p)
        else:
            k = rng.randrange(-1, n + 1)
            new, vertex = tree.jump(u, v, k, version)
            assert vertex == (p[k] if 0 <= k < len(p) else -1)
        assert new == len(versions)
        versions.append((next_edges, next_values))
        before = tree.node_count()
        assert tree.tolist(new) == next_values
        assert tree.tolist(version) == values
        assert tree.get(u, version) == values[u]
        assert tree.node_count() == before
    assert str(tree) == str(versions[-1][1])


def test_long_path_branch_reuse_and_invalid_forest():
    n = 3000
    tree = PersistentLinkCutTree(range(n), edges=((i - 1, i) for i in range(1, n)))
    adapted, total = tree.prod(0, n - 1, 0)
    assert total == n * (n - 1) // 2
    for base in (0, adapted, 0, adapted):
        version, total = tree.prod(n - 1, 0, base)
        assert total == n * (n - 1) // 2
        changed = tree.set(7, -7, version)
        assert tree.prod(0, n - 1, changed)[1] == total - 14
    for edges in ([(0, 0)], [(0, 1), (0, 1)], [(0, 1), (1, 2), (2, 0)]):
        with pytest.raises(ValueError):
            PersistentLinkCutTree([0] * 3, edges=edges)
    with pytest.raises(IndexError):
        tree.get(-1)
    assert PersistentLinkCutTree([]).tolist() == []
