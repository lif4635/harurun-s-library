import collections
import random

from library_codex.tree.IncrementalForest import IncrementalForest


def test_incremental_forest_against_bfs_paths():
    rng = random.Random(113)
    for n in range(1, 100):
        forest = IncrementalForest(n)
        graph = [[] for _ in range(n)]
        for _ in range(500):
            first = rng.randrange(n)
            second = rng.randrange(n)
            queue = collections.deque([first])
            parent = {first: -1}
            while queue:
                vertex = queue.popleft()
                for neighbor in graph[vertex]:
                    if neighbor not in parent:
                        parent[neighbor] = vertex
                        queue.append(neighbor)
            if second not in parent:
                edge = forest.add_edge(first, second)
                assert edge >= 0
                graph[first].append(second)
                graph[second].append(first)
            else:
                assert forest.add_edge(first, second) == -1
            for _ in range(10):
                source = rng.randrange(n)
                target = rng.randrange(n)
                queue = collections.deque([source])
                parent = {source: -1}
                while queue and target not in parent:
                    vertex = queue.popleft()
                    for neighbor in graph[vertex]:
                        if neighbor not in parent:
                            parent[neighbor] = vertex
                            queue.append(neighbor)
                if target not in parent:
                    assert forest.distance(source, target) == -1
                    continue
                path = []
                vertex = target
                while vertex >= 0:
                    path.append(vertex)
                    if vertex == source:
                        break
                    vertex = parent[vertex]
                path.reverse()
                assert forest.distance(source, target) == len(path) - 1
                for index, vertex in enumerate(path):
                    assert forest.kth_on_path(source, target, index) == vertex
