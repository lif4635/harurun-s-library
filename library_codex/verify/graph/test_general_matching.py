import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph_matching.GeneralMatching import GeneralMatching


def brute(n, edges):
    best = -1
    essential = 0
    for mask in range(1 << len(edges)):
        used = 0
        count = 0
        for index, (first, second) in enumerate(edges):
            if mask >> index & 1:
                vertices = (1 << first) | (1 << second)
                if used & vertices:
                    break
                used |= vertices
                count += 1
        else:
            if count > best:
                best = count
                essential = used
            elif count == best:
                essential &= used
    return best, [bool(essential >> vertex & 1) for vertex in range(n)]


def test_random_against_all_matchings():
    rng = random.Random(30)
    for n in range(10):
        possible = [(first, second) for first in range(n)
                    for second in range(first + 1, n)]
        for _ in range(400):
            rng.shuffle(possible)
            edges = possible[:rng.randrange(min(12, len(possible)) + 1)]
            graph = [[] for _ in range(n)]
            for first, second in edges:
                graph[first].append(second)
                graph[second].append(first)
            size, essential = brute(n, edges)
            matching = GeneralMatching(graph)
            assert matching.matching_size == size
            assert matching.essential_vertices() == essential
            assert len(matching.pairs()) == size
            for first, second in matching.pairs():
                assert first in graph[second]
                assert matching.mate[first] == second
                assert matching.mate[second] == first


def test_long_path_without_recursion():
    n = 100000
    graph = [[] for _ in range(n)]
    for vertex in range(n - 1):
        graph[vertex].append(vertex + 1)
        graph[vertex + 1].append(vertex)
    matching = GeneralMatching(graph)
    assert matching.matching_size == n // 2
    assert all(matching.essential_vertices())
