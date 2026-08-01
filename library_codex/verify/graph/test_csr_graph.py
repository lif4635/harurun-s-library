import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.graph.CSRGraph import (
    CSRGraph,
    CSRLowLink,
    CSRStronglyConnectedComponents,
    bfs_csr,
    bipartite_coloring_csr,
    connected_components_csr,
    dijkstra_csr,
    scc_ids_csr,
    topological_sort_csr,
    zero_one_bfs_csr,
)
from library_codex.graph.LowLink import LowLink
from library_codex.graph.ShortestPath import (
    bfs,
    bipartite_coloring,
    connected_components,
    dijkstra,
    topological_sort,
    zero_one_bfs,
)
from library_codex.graph.StronglyConnectedComponents import StronglyConnectedComponents


def adjacency(n, edges, directed=True):
    graph = [[] for _ in range(n)]
    for source, target, weight in edges:
        graph[source].append((target, weight))
        if not directed:
            graph[target].append((source, weight))
    return graph


def test_csr_layout_transpose_and_edge_ids():
    edges = [(0, 1, 4), (2, 0, 7), (0, 1, 9), (1, 1, 3)]
    graph = CSRGraph(3, edges)
    assert [list(graph.neighbors(v)) for v in range(3)] == [
        [(1, 4, 0), (1, 9, 2)],
        [(1, 3, 3)],
        [(0, 7, 1)],
    ]
    reverse = graph.transpose()
    assert [list(reverse.neighbors(v)) for v in range(3)] == [
        [(2, 7, 1)],
        [(0, 4, 0), (0, 9, 2), (1, 3, 3)],
        [],
    ]
    undirected = CSRGraph(3, edges, directed=False)
    assert undirected.arc_count == 2 * len(edges)
    assert sum(1 for row in range(3) for _ in undirected.neighbors(row)) == 8


def test_csr_from_symmetric_undirected_adjacency():
    adjacency = [
        [(1, 4), (1, 9)],
        [(0, 4), (0, 9), (1, 3), (1, 3), (2, 5)],
        [(1, 5)],
    ]
    graph = CSRGraph.from_adjacency(adjacency, directed=False)
    assert not graph.directed
    assert graph.m == 4
    assert graph.arc_count == sum(map(len, adjacency))
    assert sorted(graph.weight) == [3, 3, 4, 4, 5, 5, 9, 9]
    assert all(graph.edge_id.count(edge) == 2 for edge in range(graph.m))

    broken = [[1], []]
    try:
        CSRGraph.from_adjacency(broken, directed=False)
    except ValueError:
        pass
    else:
        raise AssertionError("asymmetric undirected adjacency must fail")


def test_csr_shortest_paths_random_against_existing():
    rng = random.Random(8201)
    for n in range(1, 100):
        edges = [
            (rng.randrange(n), rng.randrange(n), rng.randrange(30))
            for _ in range(rng.randrange(4 * n + 1))
        ]
        plain = adjacency(n, edges)
        graph = CSRGraph(n, edges)
        for start in rng.sample(range(n), min(n, 4)):
            assert dijkstra_csr(graph, start)[0] == dijkstra(plain, start)[0]

        binary_edges = [(u, v, w & 1) for u, v, w in edges]
        binary_plain = adjacency(n, binary_edges)
        binary_graph = CSRGraph(n, binary_edges)
        start = rng.randrange(n)
        assert zero_one_bfs_csr(binary_graph, start)[0] == zero_one_bfs(binary_plain, start)[0]
        unweighted = [[target for target, _ in row] for row in plain]
        assert bfs_csr(graph, start)[0] == bfs(unweighted, start)[0]


def test_csr_topological_components_and_bipartite():
    rng = random.Random(8204)
    for n in range(1, 120):
        permutation = list(range(n))
        rng.shuffle(permutation)
        position = [0] * n
        for index, vertex in enumerate(permutation):
            position[vertex] = index
        dag_edges = []
        for _ in range(rng.randrange(5 * n + 1)):
            first = rng.randrange(n)
            second = rng.randrange(n)
            if position[first] < position[second]:
                dag_edges.append((first, second, 1))
        dag = CSRGraph(n, dag_edges)
        plain_dag = adjacency(n, dag_edges)
        order = topological_sort_csr(dag)
        assert order is not None
        assert all(order.index(u) < order.index(v) for u, v, _ in dag_edges)
        assert topological_sort_csr(dag, True) == topological_sort(plain_dag, True)

        edges = [
            (rng.randrange(n), rng.randrange(n), 1)
            for _ in range(rng.randrange(4 * n + 1))
        ]
        graph = CSRGraph(n, edges, directed=False)
        plain = adjacency(n, edges, directed=False)
        component, groups = connected_components_csr(graph)
        expected_component, expected_groups = connected_components(plain)
        assert len(groups) == len(expected_groups)
        for first in range(n):
            for second in range(n):
                assert (component[first] == component[second]) == (
                    expected_component[first] == expected_component[second]
                )
        color = bipartite_coloring_csr(graph)
        expected_color = bipartite_coloring(plain)
        assert (color is None) == (expected_color is None)
        if color is not None:
            assert all(color[u] != color[v] for u, v, _ in edges)

    cyclic = CSRGraph(3, [(0, 1), (1, 2), (2, 0)])
    assert topological_sort_csr(cyclic) is None


def test_csr_scc_random_against_existing():
    rng = random.Random(8202)
    for n in range(1, 120):
        edges = [
            (rng.randrange(n), rng.randrange(n), 1)
            for _ in range(rng.randrange(6 * n + 1))
        ]
        plain = adjacency(n, edges)
        graph = CSRGraph(n, edges)
        expected = StronglyConnectedComponents(plain)
        result = CSRStronglyConnectedComponents(graph)
        count, component = scc_ids_csr(graph)
        assert count == result.count
        assert component == result.component
        for first in range(n):
            for second in range(n):
                assert result.same(first, second) == expected.same(first, second)
        assert sorted(v for group in result.groups for v in group) == list(range(n))
        assert all(group < other for group, row in enumerate(result.dag) for other in row)


def test_csr_lowlink_random_multigraph_against_existing():
    rng = random.Random(8203)
    for n in range(9):
        for _ in range(800):
            edges = [] if n == 0 else [
                (rng.randrange(n), rng.randrange(n))
                for _ in range(rng.randrange(18))
            ]
            expected = LowLink(n, edges)
            result = CSRLowLink(n, edges)
            assert result.order == expected.order
            assert result.low == expected.low
            assert result.parent == expected.parent
            assert result.parent_edge == expected.parent_edge
            assert result.is_bridge == expected.is_bridge
            assert result.is_articulation == expected.is_articulation
            assert set(result.bridge_ids) == set(expected.bridge_ids)


def test_csr_deep_paths_without_recursion():
    n = 100000
    directed_edges = [(vertex, vertex + 1, 1) for vertex in range(n - 1)]
    graph = CSRGraph(n, directed_edges)
    assert dijkstra_csr(graph)[0][-1] == n - 1
    assert bfs_csr(graph)[0][-1] == n - 1
    solver = CSRStronglyConnectedComponents(graph, build_dag=False)
    assert solver.count == n
    lowlink = CSRLowLink(n, ((v, v + 1) for v in range(n - 1)))
    assert len(lowlink.bridge_ids) == n - 1
    assert lowlink.articulation == list(range(1, n - 1))
