import heapq
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.DijkstraRadixHeap import (
    dijkstra_radix_heap,
    dijkstra_radix_heap_restore,
    restore_path,
)


def dijkstra_heapq(edge, start):
    dist = [-1] * len(edge)
    dist[start] = 0
    que = [(0, start)]
    while que:
        d, u = heapq.heappop(que)
        if d != dist[u]:
            continue
        for v, w in edge[u]:
            nd = d + w
            if dist[v] < 0 or nd < dist[v]:
                dist[v] = nd
                heapq.heappush(que, (nd, v))
    return dist


def test_random_graphs():
    for n in range(1, 100):
        edge = [[] for _ in range(n)]
        for _ in range(n * 5):
            u = random.randrange(n)
            v = random.randrange(n)
            w = random.choice((0, random.randrange(1000), random.getrandbits(200)))
            edge[u].append((v, w))
        start = random.randrange(n)
        want = dijkstra_heapq(edge, start)
        assert dijkstra_radix_heap(edge, start) == want
        dist, parent = dijkstra_radix_heap_restore(edge, start)
        assert dist == want
        for v in range(n):
            if dist[v] < 0:
                assert parent[v] == -1
                continue
            path = restore_path(parent, v)
            assert path[0] == start and path[-1] == v
            cost = 0
            for u, x in zip(path, path[1:]):
                weights = [w for y, w in edge[u] if y == x and dist[u] + w == dist[x]]
                assert weights
                cost += weights[0]
            assert cost == dist[v]
        goal = random.randrange(n)
        assert dijkstra_radix_heap(edge, start, goal) == want[goal]


def test_long_path_without_recursion():
    n = 100000
    edge = [[] for _ in range(n)]
    for i in range(n - 1):
        edge[i].append((i + 1, (i & 15) + 1))
    dist = dijkstra_radix_heap(edge)
    assert dist[-1] == sum((i & 15) + 1 for i in range(n - 1))


if __name__ == "__main__":
    random.seed(0)
    test_random_graphs()
    test_long_path_without_recursion()
