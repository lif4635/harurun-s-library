import random

from library_codex.graph_connectivity.BipartiteColoring import find_odd_cycle
from library_codex.graph_enumeration.MaximalIndependentSets import maximal_independent_sets


def _masks_from_generator(graph):
    result = set()
    for vertices in maximal_independent_sets(graph):
        result.add(sum(1 << vertex for vertex in vertices))
    return result


def _brute_maximal(graph):
    n = len(graph)
    adjacency = [sum(1 << other for other in row) for row in graph]
    result = set()
    for mask in range(1 << n):
        if any(mask >> vertex & 1 and adjacency[vertex] & mask for vertex in range(n)):
            continue
        if all(mask >> vertex & 1 or adjacency[vertex] & mask for vertex in range(n)):
            result.add(mask)
    return result


def test_maximal_independent_sets_random_against_subsets():
    random.seed(20260820)
    for n in range(9):
        for _ in range(180):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(first + 1, n):
                    if random.randrange(3) == 0:
                        graph[first].append(second)
                        graph[second].append(first)
            assert _masks_from_generator(graph) == _brute_maximal(graph)


def _has_edge(graph, first, second):
    return second in graph[first]


def test_odd_cycle_random_and_bipartite_graphs():
    random.seed(20260821)
    for n in range(1, 16):
        for _ in range(150):
            graph = [[] for _ in range(n)]
            for first in range(n):
                for second in range(first + 1, n):
                    if random.randrange(5) == 0:
                        graph[first].append(second)
                        graph[second].append(first)
            cycle = find_odd_cycle(graph)
            if cycle:
                assert len(cycle) & 1
                assert len(set(cycle)) == len(cycle)
                assert all(_has_edge(graph, cycle[i], cycle[(i + 1) % len(cycle)])
                           for i in range(len(cycle)))
            else:
                color = [-1] * n
                for start in range(n):
                    if color[start] >= 0:
                        continue
                    color[start] = 0
                    stack = [start]
                    while stack:
                        vertex = stack.pop()
                        for other in graph[vertex]:
                            if color[other] < 0:
                                color[other] = color[vertex] ^ 1
                                stack.append(other)
                            else:
                                assert color[other] != color[vertex]
    assert find_odd_cycle([[0]]) == [0]
