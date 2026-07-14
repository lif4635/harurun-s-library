import random

from library_codex.graph.ShortestPath import (
    INF,
    bellman_ford,
    bfs,
    bipartite_coloring,
    connected_components,
    dijkstra,
    restore_path,
    topological_sort,
    warshall_floyd,
    zero_one_bfs,
)
from library_codex.graph.StronglyConnectedComponents import (
    StronglyConnectedComponents,
)


def test_shortest_path_random_against_floyd():
    rng = random.Random(591720)
    for size in range(1, 40):
        graph = [[] for _ in range(size)]
        matrix = [[INF] * size for _ in range(size)]
        for node in range(size):
            matrix[node][node] = 0
        for first in range(size):
            for second in range(size):
                if first != second and rng.randrange(5) == 0:
                    weight = rng.randrange(20)
                    graph[first].append((second, weight))
                    matrix[first][second] = min(matrix[first][second], weight)
        expected = warshall_floyd(matrix)
        for start in range(size):
            distance, previous = dijkstra(graph, start)
            assert distance == expected[start]
            for goal in range(size):
                path = restore_path(previous, goal, start)
                if expected[start][goal] == INF:
                    assert path == []
                else:
                    assert path[0] == start and path[-1] == goal


def test_zero_one_bfs_and_bfs_random():
    rng = random.Random(729015)
    for size in range(1, 100):
        graph = [[] for _ in range(size)]
        unweighted = [[] for _ in range(size)]
        for first in range(size):
            for second in range(size):
                if rng.randrange(20) == 0:
                    weight = rng.randrange(2)
                    graph[first].append((second, weight))
                    unweighted[first].append(second)
        start = rng.randrange(size)
        assert zero_one_bfs(graph, start)[0] == dijkstra(graph, start)[0]
        bfs_distance, _ = bfs(unweighted, start)
        dijkstra_distance, _ = dijkstra(unweighted, start)
        assert all(
            first == (-1 if second == INF else second)
            for first, second in zip(bfs_distance, dijkstra_distance)
        )


def test_bellman_ford_negative_cycle_reachability():
    edges = [
        (0, 1, 2),
        (1, 2, 3),
        (2, 1, -5),
        (2, 3, 1),
        (4, 5, -10),
        (5, 4, 0),
    ]
    distance, previous, negative = bellman_ford(6, edges, 0)
    assert distance[0] == 0
    assert list(negative) == [0, 1, 1, 1, 0, 0]
    assert distance[1] == distance[2] == distance[3] == -INF
    assert previous[0] == -1


def test_scc_random_against_reachability():
    rng = random.Random(810246)
    for size in range(1, 80):
        graph = [[] for _ in range(size)]
        reach = [[False] * size for _ in range(size)]
        for node in range(size):
            reach[node][node] = True
        for first in range(size):
            for second in range(size):
                if rng.randrange(10) == 0:
                    graph[first].append(second)
                    reach[first][second] = True
        for middle in range(size):
            for first in range(size):
                if reach[first][middle]:
                    for second in range(size):
                        reach[first][second] |= reach[middle][second]
        solver = StronglyConnectedComponents(graph)
        for first in range(size):
            for second in range(size):
                assert solver.same(first, second) == (
                    reach[first][second] and reach[second][first]
                )
        assert sorted(vertex for group in solver.groups for vertex in group) == list(range(size))
        assert topological_sort(solver.dag) is not None


def test_topological_components_and_bipartite():
    dag = [[1, 2], [3], [3], []]
    order = topological_sort(dag, True)
    assert order == [0, 1, 2, 3]
    assert topological_sort([[1], [0]]) is None
    graph = [[1], [0], [3, 4], [2], [2]]
    component, groups = connected_components(graph)
    assert len(groups) == 2
    assert component[0] == component[1] != component[2]
    color = bipartite_coloring(graph)
    assert all(color[first] != color[second] for first, row in enumerate(graph) for second in row)
    assert bipartite_coloring([[1, 2], [0, 2], [0, 1]]) is None


def test_shortest_path_and_scc_deep_without_recursion():
    size = 100000
    graph = [[] for _ in range(size)]
    for node in range(size - 1):
        graph[node].append((node + 1, 1))
    distance, previous = dijkstra(graph)
    assert distance[-1] == size - 1
    assert len(restore_path(previous, size - 1, 0)) == size
    solver = StronglyConnectedComponents(graph)
    assert solver.count == size
