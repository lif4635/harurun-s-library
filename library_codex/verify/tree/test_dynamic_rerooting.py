import random

from library_codex.tree.DynamicRerooting import DynamicRerooting


def _component(graph, start, blocked=None):
    seen = {start}
    stack = [start]
    while stack:
        vertex = stack.pop()
        for other in graph[vertex]:
            if blocked is not None and {vertex, other} == set(blocked):
                continue
            if other not in seen:
                seen.add(other)
                stack.append(other)
    return seen


def test_dynamic_rerooting_sum_under_links_cuts_and_updates():
    rng = random.Random(442)
    for size in range(1, 80):
        weights = [rng.randrange(-100, 101) for _ in range(size)]
        structure = DynamicRerooting(
            weights,
            vertex=lambda info: info,
            compress=lambda parent, child: parent + child,
            rake=lambda first, second: first + second,
            add_edge=lambda path: path,
            add_vertex=lambda point, info: point + info,
        )
        graph = [set() for _ in range(size)]
        edges = []
        for vertex in range(1, size):
            parent = rng.randrange(vertex)
            structure.add_edge(vertex, parent)
            graph[vertex].add(parent)
            graph[parent].add(vertex)
            edges.append((vertex, parent))
        for _ in range(500):
            action = rng.randrange(5)
            if action == 0:
                vertex = rng.randrange(size)
                weights[vertex] = rng.randrange(-100, 101)
                structure.set_info(vertex, weights[vertex])
            elif action == 1 and edges:
                edge_index = rng.randrange(len(edges))
                first, second = edges.pop(edge_index)
                structure.delete_edge(first, second)
                graph[first].remove(second)
                graph[second].remove(first)
                first_component = list(_component(graph, first))
                second_component = list(_component(graph, second))
                left = rng.choice(first_component)
                right = rng.choice(second_component)
                structure.add_edge(left, right)
                graph[left].add(right)
                graph[right].add(left)
                edges.append((left, right))
            elif action == 2:
                root = rng.randrange(size)
                assert structure.query(root) == sum(weights)
            else:
                root = rng.randrange(size)
                vertex = rng.randrange(size)
                if root == vertex:
                    expected_vertices = set(range(size))
                else:
                    parent = [-1] * size
                    order = [root]
                    for current in order:
                        for other in graph[current]:
                            if other != parent[current]:
                                parent[other] = current
                                order.append(other)
                    expected_vertices = _component(
                        graph, vertex, (vertex, parent[vertex])
                    )
                assert structure.query_subtree(root, vertex) == sum(
                    weights[index] for index in expected_vertices
                )

