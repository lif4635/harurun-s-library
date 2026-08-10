from collections import deque
from random import Random

from library_codex.graph_connectivity.Reachability import reachability


def _brute(graph, source, target):
    seen = bytearray(len(graph))
    seen[source] = 1
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for entry in graph[vertex]:
            to = entry if isinstance(entry, int) else entry[0]
            if not seen[to]:
                seen[to] = 1
                queue.append(to)
    return bool(seen[target])


def test_reachability_matches_bfs_on_random_directed_graphs():
    rng = Random(1701)
    for n in range(1, 20):
        for _ in range(35):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(n):
                    if rng.randrange(7) == 0:
                        edge = second if rng.randrange(2) else (second, 5)
                        graph[first].append(edge)
            queries = [
                (rng.randrange(n), rng.randrange(n)) for _ in range(80)
            ]
            assert reachability(graph, queries) == [
                _brute(graph, source, target) for source, target in queries
            ]


def test_reachability_empty_queries():
    assert reachability([[], []], []) == []
