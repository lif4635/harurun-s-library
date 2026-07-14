import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.NamoriDecomposition import (
    Namori,
    NamoriDecomposition,
    NamoriForest,
)


def component_labels(n, edges, skip_edge=-1):
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, _) in enumerate(edges):
        if edge_id == skip_edge:
            continue
        graph[u].append(v)
        graph[v].append(u)
    component = [-1] * n
    count = 0
    for root in range(n):
        if component[root] != -1:
            continue
        component[root] = count
        stack = [root]
        while stack:
            v = stack.pop()
            for to in graph[v]:
                if component[to] == -1:
                    component[to] = count
                    stack.append(to)
        count += 1
    return count, component


def simple_path_weights(n, edges, start, goal, use_weights=True):
    if start == goal:
        return [0]
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        graph[u].append((v, edge_id, weight))
        graph[v].append((u, edge_id, weight))
    result = []
    stack = [(start, 1 << start, 0)]
    while stack:
        v, used, distance = stack.pop()
        for to, _, weight in graph[v]:
            if used >> to & 1:
                continue
            next_distance = distance + (weight if use_weights else 1)
            if to == goal:
                result.append(next_distance)
            else:
                stack.append((to, used | 1 << to, next_distance))
    return sorted(result)


def validate(n, edges):
    base_count, expected_component = component_labels(n, edges)
    expected_cycle_edge = [
        component_labels(n, edges, edge_id)[0] == base_count
        for edge_id in range(len(edges))
    ]
    expected_on_cycle = [False] * n
    for edge_id, (u, v, _) in enumerate(edges):
        if expected_cycle_edge[edge_id]:
            expected_on_cycle[u] = expected_on_cycle[v] = True

    namori = NamoriDecomposition(n, edges)
    assert namori.is_cycle_edge == expected_cycle_edge
    assert namori.on_cycle == expected_on_cycle
    assert sorted(v for group in namori.components for v in group) == list(range(n))
    for u in range(n):
        assert namori.incycle(u) == expected_on_cycle[u]
        assert namori.idx(namori.root(u))[1] == 0
        for v in range(n):
            assert namori.same_component(u, v) == (
                expected_component[u] == expected_component[v]
            )
            weighted = simple_path_weights(n, edges, u, v)
            unweighted = simple_path_weights(n, edges, u, v, False)
            expected_weighted = (
                (None, None) if not weighted else
                (weighted[0], None if len(weighted) == 1 else weighted[1])
            )
            expected_unweighted = (
                (None, None) if not unweighted else
                (unweighted[0], None if len(unweighted) == 1 else unweighted[1])
            )
            assert len(weighted) <= 2
            assert namori.dist(u, v) == expected_weighted
            assert namori.hop_distances(u, v) == expected_unweighted
            assert namori.distance(u, v) == expected_weighted[0]
            if namori.same_tree(u, v):
                assert namori.tree_distance(u, v) == expected_weighted[0]
                hops = namori.tree_hops(u, v)
                assert namori.jump_tree(u, v, 0) == u
                assert namori.jump_tree(u, v, hops) == v
            else:
                assert namori.lca(u, v) == -1

    seen_cycle_edges = []
    for cycle, edge_ids in zip(namori.cycles, namori.cycle_edge_ids):
        assert len(cycle) == len(edge_ids)
        for i, edge_id in enumerate(edge_ids):
            u, v, _ = edges[edge_id]
            assert {u, v} == {cycle[i], cycle[(i + 1) % len(cycle)]}
        seen_cycle_edges.extend(edge_ids)
    assert sorted(seen_cycle_edges) == [
        edge_id for edge_id, value in enumerate(expected_cycle_edge) if value
    ]


def test_handmade_multigraphs():
    validate(0, [])
    validate(4, [(0, 1, 2), (1, 2, -3)])
    validate(4, [(0, 0, 5), (0, 1, 2), (1, 2, 4)])
    validate(4, [(0, 1, 7), (0, 1, 11), (1, 2, 3)])
    validate(7, [
        (0, 1, 2), (1, 2, 3), (2, 0, 5), (1, 3, 7),
        (4, 5, 11), (5, 6, 13),
    ])
    assert Namori is NamoriDecomposition
    assert NamoriForest is NamoriDecomposition


def test_random_against_all_simple_paths():
    rng = random.Random(0)
    for _ in range(3000):
        n = rng.randrange(9)
        edges = []
        parent = list(range(n))

        def leader(v):
            while parent[v] != v:
                v = parent[v]
            return v

        for v in range(1, n):
            if rng.randrange(4):
                u = rng.randrange(v)
                edges.append((u, v, rng.randrange(-5, 11)))
                u = leader(u)
                w = leader(v)
                parent[w] = u
        groups = {}
        for v in range(n):
            root = leader(v)
            groups.setdefault(root, []).append(v)
        for group in groups.values():
            if rng.randrange(2):
                u = rng.choice(group)
                v = rng.choice(group)
                edges.append((u, v, rng.randrange(-5, 11)))
        validate(n, edges)


def test_rejects_more_than_one_cycle():
    try:
        NamoriDecomposition(3, [(0, 1), (1, 2), (2, 0), (0, 0)])
    except ValueError:
        pass
    else:
        assert False


def test_deep_graph_without_recursion():
    n = 100000
    namori = NamoriDecomposition(
        n, ((0, 0, 3), *((v, v + 1, 2) for v in range(n - 1)))
    )
    assert namori.cycles == [[0]]
    assert namori.cycle_edge_ids == [[0]]
    assert namori.root(n - 1) == 0
    assert namori.dist(0, n - 1) == (2 * (n - 1), None)
    assert namori.lca(0, n - 1) == 0
    assert sum(right - left for left, right in namori.path(0, n - 1)) == n
    ordered = []
    for left, right, reverse in namori.path_ordered(n - 1, 0):
        part = namori.rev[left:right]
        ordered.extend(reversed(part) if reverse else part)
    assert ordered == list(range(n - 1, -1, -1))
    assert namori.subtree(0) == (0, n)


if __name__ == "__main__":
    test_handmade_multigraphs()
    test_random_against_all_simple_paths()
    test_rejects_more_than_one_cycle()
    test_deep_graph_without_recursion()
