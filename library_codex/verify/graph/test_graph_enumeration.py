import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.GraphEnumeration import (  # noqa: E402
    chromatic_number,
    count_c4_per_edge,
    enumerate_cliques,
    enumerate_triangles,
    graph_from_edges,
    maximum_independent_set,
    maximum_independent_set_mask,
    maximum_weight_independent_set,
)


def _brute_chromatic(graph):
    n = len(graph)
    if n == 0:
        return 0
    color = [-1] * n
    for k in range(1, n + 1):
        stack = [(0, 0)]
        while stack:
            v, next_color = stack.pop()
            if v == n:
                return k
            if next_color == k:
                color[v] = -1
                continue
            stack.append((v, next_color + 1))
            if all(color[u] != next_color for u in graph[v] if u < v):
                color[v] = next_color
                stack.append((v + 1, 0))
    return n


def _is_independent(mask, graph):
    for v, neighbors in enumerate(graph):
        if mask >> v & 1:
            for u in neighbors:
                if u > v and mask >> u & 1:
                    return False
    return True


def test_chromatic_number_against_bruteforce():
    rng = random.Random(0)
    for n in range(9):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            edges = [edge for edge in pairs if rng.randrange(2)]
            graph = graph_from_edges(n, edges)
            expected = _brute_chromatic(graph)
            assert chromatic_number(graph) == expected
            assert chromatic_number(graph, exact=True) == expected


def test_maximum_independent_set_against_all_subsets():
    rng = random.Random(1)
    for n in range(11):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(100):
            graph = graph_from_edges(
                n, [edge for edge in pairs if rng.randrange(3) == 0]
            )
            expected = max(mask.bit_count() for mask in range(1 << n)
                           if _is_independent(mask, graph))
            size, mask = maximum_independent_set_mask(graph)
            vertices = maximum_independent_set(graph)
            assert size == expected == len(vertices) == mask.bit_count()
            assert _is_independent(mask, graph)


def test_maximum_weight_independent_set_against_all_subsets():
    rng = random.Random(2)
    for n in range(10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            graph = graph_from_edges(
                n, [edge for edge in pairs if rng.randrange(3) == 0]
            )
            weight = [rng.randrange(-5, 11) for _ in range(n)]
            expected = max(
                sum(weight[v] for v in range(n) if mask >> v & 1)
                for mask in range(1 << n) if _is_independent(mask, graph)
            )
            value, mask = maximum_weight_independent_set(graph, weight)
            assert value == expected
            assert value == sum(weight[v] for v in range(n) if mask >> v & 1)
            assert _is_independent(mask, graph)


def test_triangle_enumeration_vertices_edges_and_callback():
    rng = random.Random(3)
    for n in range(1, 20):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(30):
            edges = [edge for edge in pairs if rng.randrange(5) == 0]
            edge_id = {edge: i for i, edge in enumerate(edges)}
            expected = {
                (u, v, w)
                for u in range(n) for v in range(u + 1, n)
                for w in range(v + 1, n)
                if (u, v) in edge_id and (u, w) in edge_id
                and (v, w) in edge_id
            }
            items = enumerate_triangles(n, edges)
            actual = set()
            for u, v, w, a, b, c in items:
                actual.add(tuple(sorted((u, v, w))))
                incident = {
                    tuple(sorted(edges[a])), tuple(sorted(edges[b])),
                    tuple(sorted(edges[c])),
                }
                assert incident == {
                    tuple(sorted((u, v))), tuple(sorted((u, w))),
                    tuple(sorted((v, w))),
                }
            assert actual == expected
            called = []
            count = enumerate_triangles(
                n, edges, lambda *item: called.append(item)
            )
            assert count == len(called) == len(expected)


def test_clique_enumeration_against_all_subsets():
    rng = random.Random(4)
    for n in range(10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(60):
            edges = [edge for edge in pairs if rng.randrange(2)]
            graph = graph_from_edges(n, edges)
            edge_set = set(edges)
            expected = set()
            for mask in range(1, 1 << n):
                vertices = tuple(v for v in range(n) if mask >> v & 1)
                if all((u, v) in edge_set
                       for u, v in itertools.combinations(vertices, 2)):
                    expected.add(vertices)
            actual = {tuple(vertices) for vertices in enumerate_cliques(graph)}
            assert actual == expected
            called = []
            count = enumerate_cliques(graph, called.append, include_empty=True)
            assert count == len(called) == len(expected) + 1
            assert [] in called


def _brute_c4(n, edges, weight):
    edge_id = {edge: i for i, edge in enumerate(edges)}
    answer = [0] * len(edges)
    for vertices in itertools.combinations(range(n), 4):
        first = vertices[0]
        for tail in itertools.permutations(vertices[1:]):
            cycle = (first,) + tail
            if cycle[1] > cycle[3]:
                continue
            pairs = [tuple(sorted((cycle[i], cycle[(i + 1) & 3])))
                     for i in range(4)]
            if all(pair in edge_id for pair in pairs):
                ids = [edge_id[pair] for pair in pairs]
                for i, edge in enumerate(ids):
                    product = 1
                    for j in range(4):
                        if i != j:
                            product *= weight[ids[j]]
                    answer[edge] += product
    return answer


def test_count_c4_per_edge_weighted_against_bruteforce():
    rng = random.Random(5)
    for n in range(1, 10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(80):
            edges = [edge for edge in pairs if rng.randrange(3) == 0]
            weight = [rng.randrange(-3, 5) for _ in edges]
            assert count_c4_per_edge(n, edges, weight) == _brute_c4(
                n, edges, weight
            )
            assert count_c4_per_edge(n, edges) == _brute_c4(
                n, edges, [1] * len(edges)
            )
