from collections import deque
import random

from library_codex.graph.OnlineDynamicConnectivity import (
    OnlineDynamicConnectivity,
)


def components(vertex_count, edges):
    graph = [[] for _ in range(vertex_count)]
    for (first, second), count in edges.items():
        if count and first != second:
            graph[first].append(second)
            graph[second].append(first)
    group = [-1] * vertex_count
    sizes = []
    for start in range(vertex_count):
        if group[start] >= 0:
            continue
        group[start] = len(sizes)
        queue = deque([start])
        size = 0
        while queue:
            vertex = queue.popleft()
            size += 1
            for other in graph[vertex]:
                if group[other] < 0:
                    group[other] = group[start]
                    queue.append(other)
        sizes.append(size)
    return group, sizes


def test_online_dynamic_connectivity_random_against_bfs():
    rng = random.Random(7182934)
    for vertex_count in range(1, 31):
        solver = OnlineDynamicConnectivity(vertex_count)
        active = {}
        forest = set()
        for _ in range(10000):
            if active and rng.randrange(2):
                edge = rng.choice(list(active))
                first, second = edge
                query = solver.cut(first, second)
                active[edge] -= 1
                if active[edge] == 0:
                    del active[edge]
                if query.forest_cut != (-1, -1):
                    forest.remove(query.forest_cut)
                if query.forest_link != (-1, -1):
                    forest.add(tuple(sorted(query.forest_link)))
            else:
                first = rng.randrange(vertex_count)
                second = rng.randrange(vertex_count)
                edge = tuple(sorted((first, second)))
                linked = solver.link(first, second)
                active[edge] = active.get(edge, 0) + 1
                if linked != (-1, -1):
                    forest.add(tuple(sorted(linked)))
            group, sizes = components(vertex_count, active)
            assert solver.component_count == len(sizes)
            for _ in range(3):
                first = rng.randrange(vertex_count)
                second = rng.randrange(vertex_count)
                assert solver.connected(first, second) == (
                    group[first] == group[second]
                )
                assert solver.component_size(first) == sizes[group[first]]
            forest_group, _ = components(
                vertex_count, {edge: 1 for edge in forest}
            )
            assert all(
                (group[first] == group[second])
                == (forest_group[first] == forest_group[second])
                for first in range(vertex_count)
                for second in range(vertex_count)
            )


def test_online_dynamic_connectivity_deep_path_replacements():
    size = 100000
    solver = OnlineDynamicConnectivity(size)
    for vertex in range(size - 1):
        assert solver.link(vertex, vertex + 1) != (-1, -1)
    for vertex in range(0, size - 2, 2):
        assert solver.link(vertex, vertex + 2) == (-1, -1)
    for vertex in range(1, size - 1, 2):
        query = solver.cut(vertex, vertex + 1)
        assert query.forest_cut != (-1, -1)
        assert query.forest_link != (-1, -1)
    assert solver.connected(0, size - 1)
    assert solver.component_size(size // 2) == size
