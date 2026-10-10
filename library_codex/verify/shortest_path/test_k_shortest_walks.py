from heapq import heappop, heappush
from random import Random

import pytest

from library_codex.shortest_path.KShortestWalks import k_shortest_walks


def _brute(vertex_count, edges, source, target, k):
    graph = [[] for _ in range(vertex_count)]
    reverse = [[] for _ in range(vertex_count)]
    for start, end, cost in edges:
        graph[start].append((end, cost))
        reverse[end].append(start)
    reachable = [False] * vertex_count
    reachable[target] = True
    order = [target]
    for vertex in order:
        for predecessor in reverse[vertex]:
            if not reachable[predecessor]:
                reachable[predecessor] = True
                order.append(predecessor)
    if not reachable[source]:
        return []
    answer = []
    serial = 0
    heap = [(0, serial, source)]
    visits = [0] * vertex_count
    while heap and len(answer) < k:
        cost, _, vertex = heappop(heap)
        if visits[vertex] == k:
            continue
        visits[vertex] += 1
        if vertex == target:
            answer.append(cost)
        for to, weight in graph[vertex]:
            if not reachable[to]:
                continue
            serial += 1
            heappush(heap, (cost + weight, serial, to))
    return answer


def test_k_shortest_walks_matches_priority_queue_enumeration():
    rng = Random(7712)
    for n in range(1, 7):
        for _ in range(100):
            edges = []
            for first in range(n):
                for second in range(n):
                    if rng.randrange(5) == 0:
                        edges.append((first, second, rng.randrange(1, 7)))
            source = rng.randrange(n)
            target = rng.randrange(n)
            k = rng.randrange(1, 10)
            assert k_shortest_walks(n, edges, source, target, k) == _brute(
                n, edges, source, target, k
            )


def test_k_shortest_walks_counts_parallel_edges_and_zero_cycles():
    edges = [(0, 1, 2), (0, 1, 2), (1, 1, 0), (1, 2, 3)]
    assert k_shortest_walks(3, edges, 0, 2, 8) == [5] * 8
    assert k_shortest_walks(2, [], 0, 1, 5) == []
    assert k_shortest_walks(1, [], 0, 0, 5) == [0]


def test_k_shortest_walks_zero_cost_random_and_large_integers():
    rng = Random(88149)
    for n in range(1, 7):
        for _ in range(150):
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(4))
                     for _ in range(rng.randrange(12))]
            source, target = rng.randrange(n), rng.randrange(n)
            before = edges[:]
            assert k_shortest_walks(n, iter(edges), source, target, 8) == _brute(
                n, edges, source, target, 8
            )
            assert edges == before
    cost = 10**50
    assert k_shortest_walks(2, [(0, 1, cost), (1, 0, cost)], 0, 1, 3) == [cost, 3 * cost, 5 * cost]
    assert k_shortest_walks(1, [(0, 0, 2)], 0, 0, 4) == [0, 2, 4, 6]
    assert k_shortest_walks(1, [(0, 0, 0)], 0, 0, 5) == [0] * 5


def test_k_shortest_walks_long_path_and_errors():
    n = 20000
    edges = [(v, v + 1, 1) for v in range(n - 1)] + [(n - 1, 0, 1)]
    assert k_shortest_walks(n, edges, 0, n - 1, 4) == [n - 1 + i * n for i in range(4)]
    assert k_shortest_walks(0, [], 0, 0, 0) == []
    with pytest.raises(IndexError):
        k_shortest_walks(0, [], 0, 0, 1)
    with pytest.raises(IndexError):
        k_shortest_walks(2, [(0, 2, 1)], 0, 1, 1)
    with pytest.raises(ValueError):
        k_shortest_walks(2, [(0, 1, -1)], 0, 1, 1)
