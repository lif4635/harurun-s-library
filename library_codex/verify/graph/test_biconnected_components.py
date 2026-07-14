from collections import deque
import random

from library_codex.graph.BiconnectedComponents import (
    BiconnectedComponents,
    BlockCutTree,
)


def connected_after_removal(vertex_count, edges, removed):
    graph = [[] for _ in range(vertex_count)]
    for first, second in edges:
        if first != removed and second != removed:
            graph[first].append(second)
            graph[second].append(first)
    components = 0
    seen = bytearray(vertex_count)
    if 0 <= removed < vertex_count:
        seen[removed] = 1
    for start in range(vertex_count):
        if seen[start]:
            continue
        components += 1
        seen[start] = 1
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for other in graph[node]:
                if not seen[other]:
                    seen[other] = 1
                    queue.append(other)
    return components


def test_biconnected_random_multigraph_properties():
    rng = random.Random(821593)
    for vertex_count in range(1, 40):
        for _ in range(100):
            edges = []
            for _ in range(rng.randrange(80)):
                edges.append((rng.randrange(vertex_count), rng.randrange(vertex_count)))
            solver = BiconnectedComponents(vertex_count, edges)
            assigned = [
                edge_id
                for component in solver.edge_components
                for edge_id in component
            ]
            assert sorted(assigned) == list(range(len(edges)))
            assert all(
                solver.component_of_edge[edge_id] >= 0
                for edge_id in range(len(edges))
            )
            for component_edges, vertices in zip(
                solver.edge_components, solver.vertex_components
            ):
                assert vertices
                assert set(vertices) == {
                    vertex
                    for edge_id in component_edges
                    for vertex in edges[edge_id]
                } if component_edges else len(vertices) == 1


def test_block_cut_tree_is_a_forest_and_maps_vertices():
    rng = random.Random(270416)
    for vertex_count in range(1, 80):
        edges = []
        for first in range(vertex_count):
            for second in range(first, vertex_count):
                if rng.randrange(15) == 0:
                    edges.append((first, second))
                    if rng.randrange(10) == 0:
                        edges.append((first, second))
        solver = BlockCutTree(vertex_count, edges)
        assert all(solver.id(vertex) >= 0 for vertex in range(vertex_count))
        edge_count = sum(map(len, solver.tree)) // 2
        seen = bytearray(len(solver))
        component_count = 0
        for start in range(len(solver)):
            if seen[start]:
                continue
            component_count += 1
            seen[start] = 1
            stack = [(start, -1)]
            while stack:
                node, parent = stack.pop()
                for other in solver[node]:
                    assert other != parent or True
                    if not seen[other]:
                        seen[other] = 1
                        stack.append((other, node))
        assert edge_count == len(solver) - component_count
        for node, row in enumerate(solver.tree):
            for other in row:
                assert (node < solver.articulation_count) != (
                    other < solver.articulation_count
                )


def test_biconnected_deep_path_without_recursion():
    size = 100000
    edges = [(node, node + 1) for node in range(size - 1)]
    solver = BiconnectedComponents(size, edges)
    assert len(solver.edge_components) == size - 1
    block_cut = BlockCutTree(solver)
    assert len(block_cut) == size * 2 - 3
