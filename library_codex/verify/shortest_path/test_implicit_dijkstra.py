import random

import pytest

from library_codex.shortest_path.ImplicitDijkstra import implicit_dijkstra, implicit_shortest_path


def test_random_against_floyd_warshall():
    rng = random.Random(2129)
    for n in range(1, 20):
        for _ in range(20):
            graph = [[] for _ in range(n)]
            dist = [[0 if i == j else float("inf") for j in range(n)] for i in range(n)]
            for _ in range(3 * n):
                a, b, w = rng.randrange(n), rng.randrange(n), rng.randrange(10)
                graph[a].append((b, w))
                dist[a][b] = min(dist[a][b], w)
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
            starts = [rng.randrange(n) for _ in range(rng.randrange(4))]
            expected = {v: min(dist[s][v] for s in starts) for v in range(n)} if starts else {}
            expected = {v: d for v, d in expected.items() if d != float("inf")}
            distance, previous = implicit_dijkstra(starts, graph.__getitem__)
            assert distance == expected
            for v, u in previous.items():
                assert any(w + distance[u] == distance[v] for other, w in graph[u] if other == v)
            goal = rng.randrange(n)
            cost, path = implicit_shortest_path(starts, graph.__getitem__, lambda v: v == goal)
            assert cost == expected.get(goal, float("inf"))
            if path:
                assert path[0] in starts and path[-1] == goal
                assert sum(min(w for v, w in graph[u] if v == nxt) for u, nxt in zip(path, path[1:])) == cost
            else:
                assert goal not in expected


def test_unordered_states_and_none_goal():
    a, b = object(), object()
    graph = {"start": [(a, 1), (b, 1)], a: [(None, 2)], b: [(None, 4)], None: []}
    distance, previous = implicit_dijkstra(["start", "start"], graph.__getitem__)
    assert distance == {"start": 0, a: 1, b: 1, None: 3}
    assert implicit_shortest_path(["start"], graph.__getitem__, lambda v: v is None) == (3, ["start", a, None])
    assert implicit_shortest_path([None], graph.__getitem__, lambda v: v is None) == (0, [None])
    assert previous[None] is a


def test_lazy_generation_and_invalid_weight():
    visited = []

    def adjacent(v):
        visited.append(v)
        return [(v + 1, 1)]

    assert implicit_shortest_path([0], adjacent, lambda v: v == 10) == (10, list(range(11)))
    assert visited == list(range(10))
    assert implicit_dijkstra([], adjacent) == ({}, {})
    with pytest.raises(ValueError):
        implicit_dijkstra([0], lambda v: [(1, -1)])
