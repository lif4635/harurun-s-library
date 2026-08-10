import heapq
from random import Random

from library_codex.shortest_path.Top2Dijkstra import top2_dijkstra


def _dijkstra(graph, source):
    distance = [float("inf")] * len(graph)
    distance[source] = 0
    heap = [(0, source)]
    while heap:
        current, vertex = heapq.heappop(heap)
        if current != distance[vertex]:
            continue
        for to, weight in graph[vertex]:
            candidate = current + weight
            if candidate < distance[to]:
                distance[to] = candidate
                heapq.heappush(heap, (candidate, to))
    return distance


def test_top2_dijkstra_matches_separate_single_source_runs():
    rng = Random(3197)
    for n in range(1, 18):
        for _ in range(35):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(n):
                    if first != second and rng.randrange(8) == 0:
                        graph[first].append((second, rng.randrange(8)))
            sources = rng.sample(range(n), rng.randrange(n + 1))
            sources += sources[:rng.randrange(len(sources) + 1)]
            actual = top2_dijkstra(graph, sources)
            distances = {
                source: _dijkstra(graph, source) for source in set(sources)
            }
            for vertex in range(n):
                expected = sorted(
                    (row[vertex], source)
                    for source, row in distances.items()
                    if row[vertex] != float("inf")
                )[:2]
                expected += [(float("inf"), -1)] * (2 - len(expected))
                assert actual[vertex] == tuple(expected)


def test_top2_dijkstra_accepts_unit_cost_vertex_entries():
    assert top2_dijkstra([[1], [2], []], [0, 2]) == [
        ((0, 0), (float("inf"), -1)),
        ((1, 0), (float("inf"), -1)),
        ((0, 2), (2, 0)),
    ]
