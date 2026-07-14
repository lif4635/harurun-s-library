import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.LowLink import LowLink, lowlink
from library_codex.graph.TwoEdgeConnectedComponents import (
    TwoEdgeConnectedComponents,
    two_edge_connected_components,
)


def connected_components(n, edges, skip_edge=-1, skip_vertex=-1, bridges=None):
    graph = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        if edge_id == skip_edge or (bridges is not None and bridges[edge_id]):
            continue
        if u == skip_vertex or v == skip_vertex:
            continue
        graph[u].append(v)
        graph[v].append(u)
    component = [-1] * n
    count = 0
    for root in range(n):
        if root == skip_vertex or component[root] != -1:
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


def validate(n, edges):
    base_count, _ = connected_components(n, edges)
    expected_bridge = [
        connected_components(n, edges, skip_edge=edge_id)[0] > base_count
        for edge_id in range(len(edges))
    ]
    expected_articulation = [
        connected_components(n, edges, skip_vertex=v)[0] > base_count
        for v in range(n)
    ]
    _, expected_component = connected_components(
        n, edges, bridges=expected_bridge
    )

    result = LowLink(n, edges)
    assert result.is_bridge == expected_bridge
    assert result.bridge_ids == [
        edge_id for edge_id in result.bridge_ids if expected_bridge[edge_id]
    ]
    assert set(result.bridge_ids) == {
        edge_id for edge_id, bridge in enumerate(expected_bridge) if bridge
    }
    assert result.is_articulation == expected_articulation
    assert result.articulation == [
        v for v, articulation in enumerate(expected_articulation) if articulation
    ]
    assert sorted(result.order) == list(range(n))
    assert lowlink(n, edges).is_bridge == expected_bridge

    tecc = TwoEdgeConnectedComponents(n, edges)
    assert tecc.num_components == len(tecc.groups)
    assert sorted(v for group in tecc.groups for v in group) == list(range(n))
    for u in range(n):
        for v in range(n):
            assert (tecc[u] == tecc[v]) == (
                expected_component[u] == expected_component[v]
            )
    assert tecc.edge_mapping == [
        -1 if expected_bridge[edge_id] else tecc.component[u]
        for edge_id, (u, _) in enumerate(edges)
    ]
    assert sum(map(len, tecc.tree)) == 2 * sum(expected_bridge)
    assert sum(expected_bridge) == tecc.num_components - base_count
    for edge_id, (u, v) in enumerate(edges):
        cu = tecc.component[u]
        cv = tecc.component[v]
        if expected_bridge[edge_id]:
            assert cu != cv and cv in tecc.tree[cu] and cu in tecc.tree[cv]
        else:
            assert cu == cv
    forest = tecc.bridge_forest(with_edge_ids=True)
    assert sorted(
        edge_id for adjacency in forest for _, edge_id in adjacency
    ) == sorted(result.bridge_ids * 2)
    assert two_edge_connected_components(n, edges).component == tecc.component


def test_handmade_multigraphs():
    validate(0, [])
    validate(5, [])
    validate(2, [(0, 1), (0, 1)])
    validate(4, [(0, 0), (0, 1), (1, 2), (1, 2), (2, 3)])
    validate(7, [
        (0, 1), (1, 2), (2, 0), (1, 3),
        (3, 4), (4, 5), (5, 3), (5, 6),
    ])

    result = LowLink(3)
    assert result.add_edge(0, 1) == 0
    assert result.add_edge(1, 2) == 1
    assert result.build().bridge_ids == [1, 0]


def test_random_against_brute():
    rng = random.Random(0)
    for _ in range(5000):
        n = rng.randrange(9)
        m = 0 if n == 0 else rng.randrange(16)
        edges = [
            (rng.randrange(n), rng.randrange(n))
            for _ in range(m)
        ]
        validate(n, edges)


def test_deep_graph_without_recursion():
    n = 100000
    tecc = TwoEdgeConnectedComponents(
        n, ((v, v + 1) for v in range(n - 1))
    )
    assert tecc.num_components == n
    assert len(tecc.lowlink.bridge_ids) == n - 1
    assert tecc.lowlink.articulation == list(range(1, n - 1))
    assert all(len(group) == 1 for group in tecc.groups)


if __name__ == "__main__":
    test_handmade_multigraphs()
    test_random_against_brute()
    test_deep_graph_without_recursion()
