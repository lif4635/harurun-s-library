from itertools import combinations
from random import Random

import pytest

from library_codex.graph.DAGAntichain import maximum_antichain
from library_codex.graph.DegreeSequence import is_graphical, realize


def _closure(graph):
    result = []
    for source in range(len(graph)):
        seen = bytearray(len(graph))
        stack = [source]
        while stack:
            vertex = stack.pop()
            for to in graph[vertex]:
                if not seen[to]:
                    seen[to] = 1
                    stack.append(to)
        result.append(seen)
    return result


def _brute_antichain_size(graph):
    closure = _closure(graph)
    answer = 0
    for mask in range(1 << len(graph)):
        selected = [v for v in range(len(graph)) if mask >> v & 1]
        if all(
            not closure[first][second] and not closure[second][first]
            for first, second in combinations(selected, 2)
        ):
            answer = max(answer, len(selected))
    return answer


def test_maximum_antichain_matches_subset_enumeration():
    rng = Random(4109)
    for n in range(9):
        for _ in range(80):
            order = list(range(n))
            rng.shuffle(order)
            graph = [[] for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.randrange(4) == 0:
                        graph[order[i]].append(order[j])
            answer = maximum_antichain(graph)
            closure = _closure(graph)
            assert len(answer) == _brute_antichain_size(graph)
            assert all(
                not closure[first][second] and not closure[second][first]
                for first, second in combinations(answer, 2)
            )


def test_maximum_antichain_rejects_cycles():
    with pytest.raises(ValueError):
        maximum_antichain([[1], [0]])


def _graphical_sequences(n):
    edges = list(combinations(range(n), 2))
    sequences = set()
    for mask in range(1 << len(edges)):
        degree = [0] * n
        for index, (first, second) in enumerate(edges):
            if mask >> index & 1:
                degree[first] += 1
                degree[second] += 1
        sequences.add(tuple(degree))
    return sequences


def test_degree_sequence_matches_exhaustive_small_graphs_and_realize():
    rng = Random(5813)
    for n in range(1, 7):
        possible = _graphical_sequences(n)
        samples = list(possible)
        samples += [tuple(rng.randrange(n + 1) for _ in range(n)) for _ in range(500)]
        for degree in samples:
            expected = degree in possible
            assert is_graphical(degree) == expected
            edges = realize(degree)
            if not expected:
                assert edges is None
                continue
            actual = [0] * n
            assert len(edges) == len(set(tuple(sorted(edge)) for edge in edges))
            for first, second in edges:
                assert first != second
                actual[first] += 1
                actual[second] += 1
            assert actual == list(degree)
