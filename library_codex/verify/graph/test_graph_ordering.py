import heapq
import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.GraphOrdering import (  # noqa: E402
    bipolar_orientation,
    optimal_tree_topological_order,
    shortest_path_without_each_edge,
)


def test_optimal_tree_topological_order_against_permutations():
    rng = random.Random(70)
    for n in range(1, 10):
        repeats = 150 if n <= 6 else 30 if n == 7 else 5 if n == 8 else 2
        for _ in range(repeats):
            parent = [-1] + [rng.randrange(v) for v in range(1, n)]
            weight0 = [rng.randrange(8) for _ in range(n)]
            weight1 = [rng.randrange(8) for _ in range(n)]
            expected = float("inf")
            for order in itertools.permutations(range(n)):
                position = [0] * n
                for i, v in enumerate(order):
                    position[v] = i
                if any(position[parent[v]] > position[v] for v in range(1, n)):
                    continue
                value = sum(weight1[order[i]] * weight0[order[j]]
                            for i in range(n) for j in range(i + 1, n))
                expected = min(expected, value)
            value, order = optimal_tree_topological_order(
                parent, weight0, weight1
            )
            position = [0] * n
            for i, v in enumerate(order):
                position[v] = i
            assert all(position[parent[v]] < position[v] for v in range(1, n))
            assert value == expected
            assert value == sum(weight1[order[i]] * weight0[order[j]]
                                for i in range(n) for j in range(i + 1, n))


def _has_st_order(graph, source, target):
    others = [v for v in range(len(graph)) if v not in (source, target)]
    for middle in itertools.permutations(others):
        order = (source,) + middle + (target,)
        position = [0] * len(graph)
        for i, v in enumerate(order):
            position[v] = i
        if (any(position[to] > 0 for to in graph[source])
                and any(position[to] < len(graph) - 1 for to in graph[target])
                and all(any(position[to] < position[v] for to in graph[v])
               and any(position[to] > position[v] for to in graph[v])
               for v in others)):
            return True
    return False


def test_bipolar_orientation_against_permutation_existence():
    rng = random.Random(71)
    for n in range(2, 9):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(150):
            edges = [edge for edge in possible if rng.randrange(2)]
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)
            source, target = rng.sample(range(n), 2)
            expected = _has_st_order(graph, source, target)
            position = bipolar_orientation(graph, source, target)
            assert (position is not None) == expected
            if position is not None:
                assert position[source] == 0 and position[target] == n - 1
                for v in range(n):
                    if v not in (source, target):
                        assert any(position[to] < position[v] for to in graph[v])
                        assert any(position[to] > position[v] for to in graph[v])


def _dijkstra_removed(n, edges, source, target, removed):
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if edge_id != removed:
            graph[u].append((v, weight))
            graph[v].append((u, weight))
    distance = [float("inf")] * n
    distance[source] = 0
    heap = [(0, source)]
    while heap:
        dist, v = heapq.heappop(heap)
        if distance[v] != dist:
            continue
        for to, weight in graph[v]:
            nxt = dist + weight
            if nxt < distance[to]:
                distance[to] = nxt
                heapq.heappush(heap, (nxt, to))
    return distance[target]


def test_replacement_shortest_paths_against_repeated_dijkstra():
    rng = random.Random(72)
    for n in range(1, 35):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(60):
            rng.shuffle(possible)
            edges = [(u, v, rng.randrange(1, 15))
                     for u, v in possible[:rng.randrange(min(80, len(possible)) + 1)]]
            if edges and rng.randrange(2):
                u, v, _ = rng.choice(edges)
                edges.append((u, v, rng.randrange(1, 15)))
            source = rng.randrange(n)
            target = rng.randrange(n)
            expected = [_dijkstra_removed(n, edges, source, target, edge_id)
                        for edge_id in range(len(edges))]
            assert shortest_path_without_each_edge(
                n, edges, source, target
            ) == expected
