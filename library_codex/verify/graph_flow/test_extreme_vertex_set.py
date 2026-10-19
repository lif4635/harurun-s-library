import random

import pytest

from library_codex.graph_flow.ExtremeVertexSet import extreme_vertex_tree


def boundary(mask, edges):
    return sum(w for u, v, w in edges if (mask >> u ^ mask >> v) & 1)


def test_all_extreme_sets_and_boundaries():
    rng = random.Random(90241)
    for n in range(1, 9):
        for _ in range(40):
            edges = [(u, v, rng.randrange(8)) for u in range(n)
                     for v in range(u) if rng.randrange(3)]
            children, costs = extreme_vertex_tree(n, iter(edges))
            assert len(children) == len(costs) == 2 * n - 1
            masks = [1 << v for v in range(n)]
            assert children[:n] == [()] * n
            for node, (u, v) in enumerate(children[n:], n):
                assert u < node and v < node
                assert masks[u] & masks[v] == 0
                masks.append(masks[u] | masks[v])
            assert masks[-1] == (1 << n) - 1
            assert costs == [boundary(mask, edges) for mask in masks]
            cut_costs = [boundary(mask, edges) for mask in range(1 << n)]
            candidates = set(masks)
            for mask in range(1, 1 << n):
                sub = mask - 1 & mask
                while sub and cut_costs[sub] > cut_costs[mask]:
                    sub = sub - 1 & mask
                if not sub:
                    assert mask in candidates


def test_parallel_edges_loops_and_disconnected():
    edges = [(0, 1, 3), (1, 0, 7), (1, 1, 900), (2, 3, 0)]
    children, costs = extreme_vertex_tree(5, edges)
    masks = [1 << v for v in range(5)]
    for u, v in children[5:]:
        masks.append(masks[u] | masks[v])
    assert costs == [boundary(mask, edges) for mask in masks]


def test_invalid_inputs():
    for n, edges in [(0, []), (2, [(0, 2, 1)]), (2, [(-1, 1, 1)]),
                     (2, [(0, 1, -1)])]:
        with pytest.raises(ValueError):
            extreme_vertex_tree(n, edges)
