import random

from library_codex.graph_connectivity.BridgeForest import BridgeForest
from library_codex.graph_connectivity.DominatorTree import DominatorTree


def _components_without_edge(n, edges, removed):
    graph = [[] for _ in range(n)]
    for edge_id, (first, second) in enumerate(edges):
        if edge_id == removed:
            continue
        graph[first].append(second)
        graph[second].append(first)
    component = [-1] * n
    for start in range(n):
        if component[start] != -1:
            continue
        component[start] = start
        queue = [start]
        for vertex in queue:
            for target in graph[vertex]:
                if component[target] == -1:
                    component[target] = start
                    queue.append(target)
    return component


def test_bridge_forest_random_against_edge_removal():
    rng = random.Random(314159)
    for n in range(1, 20):
        for _ in range(40):
            edges = []
            for first in range(n):
                for second in range(first + 1, n):
                    if rng.randrange(7) == 0:
                        edges.append((first, second))
                        if rng.randrange(12) == 0:
                            edges.append((first, second))
            bridge = BridgeForest(n, edges)
            original = _components_without_edge(n, edges, -1)
            after = [
                _components_without_edge(n, edges, edge_id)
                for edge_id in range(len(edges))
            ]
            for first in range(n):
                for second in range(n):
                    separators = [
                        edge_id for edge_id, component in enumerate(after)
                        if component[first] != component[second]
                        and original[first] == original[second]
                    ]
                    distance = bridge.bridge_distance(first, second)
                    if original[first] != original[second]:
                        assert distance == -1
                        assert bridge.bridge_path(first, second) is None
                        continue
                    path = bridge.bridge_path(first, second)
                    assert distance == len(separators) == len(path)
                    assert set(path) == set(separators)
                    for index, edge_id in enumerate(path):
                        assert bridge.kth_bridge(first, second, index) == edge_id
                    for edge_id in range(len(edges)):
                        assert bridge.is_bridge_separator(
                            edge_id, first, second
                        ) == (edge_id in separators)


def _reachable_without(graph, root, removed=-1):
    if root == removed:
        return [False] * len(graph)
    visited = [False] * len(graph)
    visited[root] = True
    queue = [root]
    for vertex in queue:
        for target in graph[vertex]:
            if target != removed and not visited[target]:
                visited[target] = True
                queue.append(target)
    return visited


def test_dominator_tree_queries_random():
    rng = random.Random(161803)
    for n in range(1, 18):
        for _ in range(30):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(n):
                    if first != second and rng.randrange(8) == 0:
                        graph[first].append(second)
            root = rng.randrange(n)
            query = DominatorTree(graph, root)
            reachable = _reachable_without(graph, root)
            without = [
                _reachable_without(graph, root, removed)
                for removed in range(n)
            ]
            for dominator in range(n):
                for vertex in range(n):
                    expected = (
                        reachable[dominator]
                        and reachable[vertex]
                        and (
                            dominator == vertex
                            or not without[dominator][vertex]
                        )
                    )
                    assert query.dominates(dominator, vertex) == expected
            for vertex in range(n):
                path = query.dominator_path(vertex)
                if not reachable[vertex]:
                    assert path == []
                    continue
                assert path[0] == root and path[-1] == vertex
                assert all(query.dominates(item, vertex) for item in path)
            for first in range(n):
                for second in range(n):
                    common = query.nearest_common_dominator(first, second)
                    if not reachable[first] or not reachable[second]:
                        assert common == -1
                    else:
                        assert query.dominates(common, first)
                        assert query.dominates(common, second)
                        assert query.depth[common] == max(
                            query.depth[vertex] for vertex in range(n)
                            if query.dominates(vertex, first)
                            and query.dominates(vertex, second)
                        )
