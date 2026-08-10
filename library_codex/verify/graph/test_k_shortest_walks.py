from heapq import heappop, heappush
from random import Random

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
    while heap and len(answer) < k:
        cost, _, vertex = heappop(heap)
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
