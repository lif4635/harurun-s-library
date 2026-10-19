import random

import pytest

from library_codex.graph_spanning.IncrementalMinimumSpanningForest import IncrementalMSF
from library_codex.benchmarks.baselines.incremental_msf_lct import incremental_msf
from library_codex.benchmarks.baselines.incremental_msf_lct import IncrementalMinimumSpanningForest as LinkCutForest


def _kruskal(n, edges):
    parent = list(range(n))
    total = 0
    count = n
    for _, u, v, weight in sorted(edges, key=lambda edge: edge[3]):
        while parent[u] != u:
            u = parent[u]
        while parent[v] != v:
            v = parent[v]
        if u != v:
            parent[u] = v
            total += weight
            count -= 1
    return total, count


@pytest.mark.parametrize("forest_class", [IncrementalMSF, LinkCutForest])
def test_random_additions_against_kruskal(forest_class):
    rng = random.Random(854901)
    for n in range(1, 25):
        forest = forest_class(n)
        edges = []
        selected = {}
        for edge_id in range(180):
            u, v, weight = rng.randrange(n), rng.randrange(n), rng.randrange(-30, 31)
            edge = (edge_id, u, v, weight)
            edges.append(edge)
            removed = forest.add(u, v, weight)
            selected[edge_id] = edge
            if removed != -1:
                del selected[removed]
            assert (forest.weight, forest.components) == _kruskal(n, edges)
            assert forest.edges() == sorted(selected.values())
            assert _kruskal(n, selected.values()) == (forest.weight, forest.components)
            assert len(forest._weights) <= 2 * n
        before = forest.edges()
        assert str(forest) == str(before)
        assert repr(forest) == f"{forest_class.__name__}(n={n}, edges={before!r})"
        forest.edges().clear()
        assert forest.edges() == before


def test_replacement_ties_and_invalid_inputs():
    forest = IncrementalMSF(3)
    assert forest.add(0, 1, 5) == -1
    assert forest.add(1, 2, 8) == -1
    assert forest.add(0, 2, 3) == 1
    assert forest.add(0, 1, 5) == 3
    assert forest.add(2, 2, -100) == 4
    assert forest.weight == 8
    assert forest.components == 1
    assert forest.add(0, 1, -(1 << 100)) == 0
    assert forest.weight == 3 - (1 << 100)
    with pytest.raises(ValueError):
        forest.add(-1, 0, 1)
    assert forest.add(0, 0, 0) == 6
    empty = IncrementalMSF(0)
    assert empty.edges() == [] and empty.weight == empty.components == 0
    with pytest.raises(ValueError):
        empty.add(0, 0, 0)
    with pytest.raises(ValueError):
        IncrementalMSF(-1)


def test_long_chain_and_reused_edge_storage():
    n = 10000
    forest = IncrementalMSF(n)
    for i in range(n - 1):
        assert forest.add(i, i + 1, i + 1) == -1
    assert forest.add(0, n - 1, -1) == n - 2
    for i in range(10000):
        assert forest.add(0, n - 1, -i - 2) == n - 1 + i
    assert len(forest._weights) == n


def test_offline_against_kruskal():
    rng = random.Random(91478)
    assert incremental_msf(0, []) == []
    for n in range(1, 30):
        for repeat in range(4):
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(-30, 31)) for _ in range(120)]
            saved = edges.copy()
            answers = incremental_msf(n, edges)
            selected = {}
            for i, (u, v, weight) in enumerate(edges):
                selected[i] = (i, u, v, weight)
                if answers[i] >= 0:
                    del selected[answers[i]]
                expected, components = _kruskal(n, [(j, *edge) for j, edge in enumerate(edges[:i + 1])])
                assert sum(edge[3] for edge in selected.values()) == expected
                assert len(selected) == n - components
                assert _kruskal(n, selected.values()) == (expected, components)
            assert edges == saved
    with pytest.raises(ValueError):
        incremental_msf(1, [(0, 1, 0)])


def test_transformed_tree_invariants():
    rng = random.Random(85414)
    for n in (2, 7, 23, 50):
        forest = IncrementalMSF(n)
        for step in range(250):
            forest.add(rng.randrange(n), rng.randrange(n), rng.randrange(-100, 101))
            if step % 11:
                continue
            parent, size, weights = forest._parent, forest._size, forest._weights
            depths = []
            counts = [0] * n
            for vertex in range(n):
                current = vertex
                seen = set()
                while current >= 0:
                    assert current not in seen
                    seen.add(current)
                    counts[current] += 1
                    current = parent[current]
                depths.append(len(seen))
            assert counts == size
            graph = [[] for _ in range(n)]
            for _, u, v, w in forest.edges():
                graph[u].append((v, w))
                graph[v].append((u, w))
            for start in range(n):
                stack = [(start, -1, None)]
                while stack:
                    target, previous, maximum = stack.pop()
                    if target != start:
                        u, v = start, target
                        a, b = depths[u], depths[v]
                        path_weights = []
                        while u != v:
                            if a >= b:
                                path_weights.append(weights[u])
                                u = parent[u]
                                a -= 1
                            else:
                                path_weights.append(weights[v])
                                v = parent[v]
                                b -= 1
                        assert max(path_weights) == maximum
                    for neighbor, w in graph[target]:
                        if neighbor != previous:
                            stack.append((neighbor, target, w if maximum is None else max(maximum, w)))
