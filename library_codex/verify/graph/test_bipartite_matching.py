import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.BipartiteMatching import (
    BipartiteMatching,
    bipartite_matching,
    maximum_bipartite_matching,
)
from library_codex.graph.MaxFlow import MaxFlowGraph


def brute(left_size, right_size, graph):
    dp = {0}
    for left in range(left_size):
        nxt = set(dp)
        for mask in dp:
            for right in graph[left]:
                if not (mask >> right & 1):
                    nxt.add(mask | 1 << right)
        dp = nxt
    return max(mask.bit_count() for mask in dp)


def validate(matcher, expected):
    pairs = matcher.pairs()
    assert len(pairs) == expected
    assert len({left for left, _ in pairs}) == expected
    assert len({right for _, right in pairs}) == expected
    assert all(right in matcher.graph[left] for left, right in pairs)

    cover_left, cover_right = matcher.minimum_vertex_cover()
    assert len(cover_left) + len(cover_right) == expected
    cover_left = set(cover_left)
    cover_right = set(cover_right)
    assert all(
        left in cover_left or right in cover_right
        for left, edges in enumerate(matcher.graph)
        for right in edges
    )

    independent_left, independent_right = matcher.maximum_independent_set()
    assert len(independent_left) + len(independent_right) == (
        matcher.left_size + matcher.right_size - expected
    )
    independent_right = set(independent_right)
    assert all(
        right not in independent_right
        for left in independent_left
        for right in matcher.graph[left]
    )

    decomposition = matcher.dulmage_mendelsohn()
    vertices = [v for group in decomposition for v in group]
    assert sorted(vertices) == list(range(matcher.left_size + matcher.right_size))
    assert len(vertices) == len(set(vertices))


def test_small_against_brute():
    for left_size in range(8):
        for right_size in range(8):
            for _ in range(1000):
                graph = [[] for _ in range(left_size)]
                matcher = BipartiteMatching(left_size, right_size)
                for left in range(left_size):
                    for right in range(right_size):
                        if random.randrange(3) == 0:
                            graph[left].append(right)
                            matcher.add_edge(left, right)
                            if random.randrange(10) == 0:
                                graph[left].append(right)
                                matcher.add_edge(left, right)
                expected = brute(left_size, right_size, graph)
                assert matcher.solve() == expected
                validate(matcher, expected)
                assert bipartite_matching(graph, right_size) == matcher.match_left
                assert len(maximum_bipartite_matching(
                    left_size, right_size,
                    [(l, r) for l, es in enumerate(graph) for r in es],
                )) == expected


def test_edge_cover_and_dynamic_add():
    matcher = BipartiteMatching(4, 4)
    for edge in ((0, 0), (0, 1), (1, 1), (2, 2), (3, 2), (3, 3)):
        matcher.add_edge(*edge)
    assert matcher.solve() == 4
    cover = matcher.minimum_edge_cover()
    assert len(cover) == 4
    assert {u for u, _ in cover} == set(range(4))
    assert {v for _, v in cover} == set(range(4))

    matcher = BipartiteMatching(2, 2)
    matcher.add_edge(0, 0)
    assert matcher.solve() == 1
    matcher.add_edge(1, 1)
    assert matcher.solve() == 2
    assert matcher.minimum_edge_cover() == matcher.pairs()

    isolated = BipartiteMatching(2, 2)
    isolated.add_edge(0, 0)
    assert isolated.minimum_edge_cover() is None


def test_random_against_maxflow():
    for _ in range(1000):
        left_size = random.randrange(1, 100)
        right_size = random.randrange(1, 100)
        matcher = BipartiteMatching(left_size, right_size)
        source = left_size + right_size
        sink = source + 1
        flow = MaxFlowGraph(sink + 1)
        for left in range(left_size):
            flow.add_edge(source, left, 1)
        for right in range(right_size):
            flow.add_edge(left_size + right, sink, 1)
        for _ in range(random.randrange(500)):
            left = random.randrange(left_size)
            right = random.randrange(right_size)
            matcher.add_edge(left, right)
            flow.add_edge(left, left_size + right, 1)
        assert matcher.solve() == flow.flow(source, sink)


def test_large_without_recursion():
    n = 100000
    matcher = BipartiteMatching(n, n)
    for left in range(n):
        for j in range(4):
            matcher.add_edge(left, (left * (j * 2 + 1) + j * 99991) % n)
    assert matcher.solve() == n
    assert len(matcher.minimum_vertex_cover()[0]) == n


def test_deep_augmenting_path_without_recursion():
    n = 100000
    matcher = BipartiteMatching(n, n)
    for left in range(n - 1):
        matcher.add_edge(left, left)
    assert matcher.solve() == n - 1

    matcher.add_edge(0, n - 1)
    for left in range(1, n):
        matcher.add_edge(left, left - 1)
    assert matcher.solve() == n
    assert matcher.match_left[0] == n - 1
    assert matcher.match_left[n - 1] == n - 2


if __name__ == "__main__":
    random.seed(0)
    test_small_against_brute()
    test_edge_cover_and_dynamic_add()
    test_random_against_maxflow()
    test_large_without_recursion()
    test_deep_augmenting_path_without_recursion()
