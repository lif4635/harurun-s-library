import heapq
import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from shortest_path.DialDijkstra import dial_dijkstra  # noqa: E402
from graph_enumeration.HeldKarp import held_karp_cycle, held_karp_path  # noqa: E402
from graph_matching.Hungarian import hungarian, hungarian_max  # noqa: E402


def test_hungarian_rectangular_against_permutations():
    rng = random.Random(10)
    for rows in range(6):
        for columns in range(max(1, rows), 7):
            for _ in range(80):
                cost = [[rng.randrange(-20, 21) for _ in range(columns)]
                        for _ in range(rows)]
                expected_min = min(
                    (sum(cost[i][p[i]] for i in range(rows)), p)
                    for p in itertools.permutations(range(columns), rows)
                ) if rows else (0, ())
                expected_max = max(
                    (sum(cost[i][p[i]] for i in range(rows)), p)
                    for p in itertools.permutations(range(columns), rows)
                ) if rows else (0, ())
                value, assignment = hungarian(cost)
                assert value == expected_min[0]
                assert len(set(assignment)) == rows
                assert value == sum(cost[i][assignment[i]] for i in range(rows))
                value, assignment = hungarian_max(cost)
                assert value == expected_max[0]
                assert len(set(assignment)) == rows
                assert value == sum(cost[i][assignment[i]] for i in range(rows))


def test_held_karp_path_and_cycle_against_permutations():
    rng = random.Random(12)
    for n in range(1, 9):
        for _ in range(30):
            distance = [[0 if u == v else rng.randrange(-5, 15)
                         for v in range(n)] for u in range(n)]
            for start in (None, rng.randrange(n)):
                goals = (None, rng.randrange(n))
                for goal in goals:
                    if start is not None and goal == start and n > 1:
                        continue
                    orders = itertools.permutations(range(n))
                    expected = min(
                        sum(distance[p[i]][p[i + 1]] for i in range(n - 1))
                        for p in orders
                        if (start is None or p[0] == start)
                        and (goal is None or p[-1] == goal)
                    )
                    value, order = held_karp_path(
                        distance, start, goal, restore=True
                    )
                    assert value == expected
                    assert sorted(order) == list(range(n))
                    assert value == sum(distance[order[i]][order[i + 1]]
                                        for i in range(n - 1))
            if n > 1:
                start = rng.randrange(n)
                expected = min(
                    sum(distance[p[i]][p[i + 1]] for i in range(n - 1))
                    + distance[p[-1]][start]
                    for p in itertools.permutations(range(n)) if p[0] == start
                )
                value, order = held_karp_cycle(distance, start, restore=True)
                assert value == expected
                assert order[0] == order[-1] == start
                assert sorted(order[:-1]) == list(range(n))


def _heap_dijkstra(graph, starts):
    n = len(graph)
    distance = [float("inf")] * n
    heap = []
    for start in starts:
        distance[start] = 0
        heapq.heappush(heap, (0, start))
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


def test_dial_dijkstra_random_and_zero_edges():
    rng = random.Random(13)
    for n in range(1, 60):
        for _ in range(20):
            maximum = rng.randrange(10)
            graph = [[] for _ in range(n)]
            for u in range(n):
                for v in range(n):
                    if rng.randrange(15) == 0:
                        graph[u].append((v, rng.randrange(maximum + 1)))
            starts = rng.sample(range(n), rng.randrange(1, min(5, n) + 1))
            expected = _heap_dijkstra(graph, starts)
            distance, parent = dial_dijkstra(
                graph, starts, maximum, restore=True
            )
            assert distance == expected
            for v in range(n):
                if parent[v] != -1:
                    assert any(to == v and distance[parent[v]] + weight == distance[v]
                               for to, weight in graph[parent[v]])
