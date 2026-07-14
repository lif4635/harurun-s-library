import heapq
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.ExpandedGraph import (  # noqa: E402
    DimensionExpandedGraph,
    RangeEdgeGraph,
    grid_to_graph,
    reverse_graph,
)


def _dijkstra(graph, start):
    distance = [float("inf")] * len(graph)
    distance[start] = 0
    heap = [(0, start)]
    while heap:
        dist, v = heapq.heappop(heap)
        if distance[v] != dist:
            continue
        for to, weight in graph[v]:
            nxt = dist + weight
            if nxt < distance[to]:
                distance[to] = nxt
                heapq.heappush(heap, (nxt, to))
    return distance


def test_range_edge_graph_against_complete_expansion():
    rng = random.Random(40)
    for n in range(1, 40):
        for _ in range(60):
            compact = RangeEdgeGraph(n)
            explicit = [[] for _ in range(n)]
            for _ in range(80):
                kind = rng.randrange(4)
                a, b = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                c, d = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                source = rng.randrange(n)
                target = rng.randrange(n)
                cost = rng.randrange(10)
                if kind == 0:
                    compact.add_point_to_point(source, target, cost)
                    explicit[source].append((target, cost))
                elif kind == 1:
                    compact.add_point_to_range(source, a, b, cost)
                    explicit[source].extend((v, cost) for v in range(a, b))
                elif kind == 2:
                    compact.add_range_to_point(a, b, target, cost)
                    for v in range(a, b):
                        explicit[v].append((target, cost))
                else:
                    compact.add_range_to_range(a, b, c, d, cost)
                    for u in range(a, b):
                        explicit[u].extend((v, cost) for v in range(c, d))
            for start in rng.sample(range(n), min(n, 5)):
                assert _dijkstra(compact.graph, start)[:n] == _dijkstra(
                    explicit, start
                )
            assert len(compact.in_id) == 2 * n - 1


def test_dimension_expanded_ids_neighbors_and_searches():
    expanded = DimensionExpandedGraph(3, 4, 5, extra=2)
    assert len(expanded) == 62
    for vertex in range(60):
        coordinate = expanded.coordinate(vertex)
        assert expanded.id(coordinate) == vertex
        assert all(sum(abs(a - b) for a, b in zip(coordinate, other)) == 1
                   for other in expanded.neighbors(coordinate))
    assert expanded.extra_id(1) == 61
    distance = expanded.bfs((0, 0, 0))
    for vertex in range(60):
        assert distance[vertex] == sum(expanded.coordinate(vertex))
    weighted = lambda v: [
        (expanded.id(to), (axis + 1) & 1)
        for to in expanded.neighbors(expanded.coordinate(v))
        for axis in [next(i for i, (a, b) in enumerate(
            zip(expanded.coordinate(v), to)) if a != b)]
    ] if v < 60 else []
    assert expanded.bfs01((0, 0, 0), weighted) == expanded.dijkstra(
        (0, 0, 0), weighted
    )


def test_reverse_and_grid_graph():
    graph = [[(1, 2), (2, 3)], [], [(1, 4)]]
    assert reverse_graph(graph) == [[], [(0, 2), (2, 4)], [(0, 3)]]
    grid = ["..#", ".#.", "..."]
    graph, to_id, coordinate = grid_to_graph(grid)
    assert to_id(2, 2) == 8 and coordinate(8) == (2, 2)
    assert sorted(graph[to_id(2, 2)]) == [to_id(1, 2), to_id(2, 1)]
    assert graph[to_id(0, 2)] == []
