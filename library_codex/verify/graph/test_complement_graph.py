from collections import deque
from random import Random

from library_codex.graph_connectivity.ComplementGraph import (
    complement_bfs,
    complement_components,
)


def _brute_bfs(graph, source):
    n = len(graph)
    adjacent = [set(row) for row in graph]
    distance = [-1] * n
    distance[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for to in range(n):
            if to != vertex and to not in adjacent[vertex] and distance[to] < 0:
                distance[to] = distance[vertex] + 1
                queue.append(to)
    return distance


def test_complement_bfs_matches_bruteforce_on_directed_graphs():
    rng = Random(8173)
    for n in range(1, 14):
        for _ in range(80):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(n):
                    if first != second and rng.randrange(4) == 0:
                        graph[first].append(second)
            source = rng.randrange(n)
            distance, parent = complement_bfs(graph, source)
            assert distance == _brute_bfs(graph, source)
            assert parent[source] == -1
            for vertex in range(n):
                if parent[vertex] != -1:
                    assert vertex not in graph[parent[vertex]]
                    assert distance[vertex] == distance[parent[vertex]] + 1


def test_complement_components_match_bruteforce_and_accept_tuples():
    rng = Random(2219)
    for n in range(12):
        for _ in range(80):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(first + 1, n):
                    if rng.randrange(3) == 0:
                        graph[first].append((second, 1))
                        graph[second].append((first, 1))
            plain = [[edge[0] for edge in row] for row in graph]
            expected = []
            unseen = set(range(n))
            while unseen:
                root = next(iter(unseen))
                distance = _brute_bfs(plain, root)
                component = {v for v, dist in enumerate(distance) if dist >= 0}
                expected.append(sorted(component))
                unseen -= component
            actual = [sorted(component) for component in complement_components(graph)]
            assert sorted(actual) == sorted(expected)
