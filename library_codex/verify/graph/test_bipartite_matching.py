import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph_matching.BipartiteMatching import BipartiteMatching
from library_codex.graph_flow.MaxFlow import MaxFlowGraph


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


def brute_essential(left_size, right_size, graph):
    best = -1
    common_left = 0
    common_right = 0

    def search(left, used_left, used_right, count):
        nonlocal best, common_left, common_right
        if left == left_size:
            if count > best:
                best = count
                common_left = used_left
                common_right = used_right
            elif count == best:
                common_left &= used_left
                common_right &= used_right
            return
        search(left + 1, used_left, used_right, count)
        for right in graph[left]:
            if not used_right >> right & 1:
                search(
                    left + 1,
                    used_left | 1 << left,
                    used_right | 1 << right,
                    count + 1,
                )

    search(0, 0, 0, 0)
    return (
        [bool(common_left >> left & 1) for left in range(left_size)],
        [bool(common_right >> right & 1) for right in range(right_size)],
    )


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


def test_essential_vertices_against_all_matchings():
    rng = random.Random(121)
    for left_size in range(7):
        for right_size in range(7):
            for _ in range(300):
                graph = [[] for _ in range(left_size)]
                matcher = BipartiteMatching(left_size, right_size)
                for left in range(left_size):
                    for right in range(right_size):
                        if rng.randrange(3) == 0:
                            graph[left].append(right)
                            matcher.add_edge(left, right)
                assert matcher.essential_vertices() == brute_essential(
                    left_size, right_size, graph
                )


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


def all_maximum_matchings(graph):
    best = []
    size = -1

    def search(remaining, edges):
        nonlocal best, size
        if not remaining:
            if len(edges) > size:
                size = len(edges)
                best = [set(edges)]
            elif len(edges) == size:
                best.append(set(edges))
            return
        u = min(remaining)
        rest = remaining - {u}
        search(rest, edges)
        for v in set(graph[u]) & rest:
            search(rest - {v}, edges + [(min(u, v), max(u, v))])

    search(set(range(len(graph))), [])
    return best


def validate_graph_input(matcher, graph):
    n = len(graph)
    best = all_maximum_matchings(graph)
    size = len(best[0])
    normalize = lambda edges: {tuple(sorted(edge)) for edge in edges}
    assert matcher.solve() == size
    assert normalize(matcher.pairs()) in best
    mate = matcher.mates()
    assert len(mate) == n
    assert sum(v != -1 for v in mate) == 2 * size
    for u, v in enumerate(mate):
        if v != -1:
            assert v in graph[u] and mate[v] == u
    expected_vertices = set.intersection(*[{v for edge in m for v in edge} for m in best])
    assert matcher.essential_vertices() == [v in expected_vertices for v in range(n)]
    assert normalize(matcher.allowed_edges()) == set.union(*best)
    assert normalize(matcher.essential_edges()) == set.intersection(*best)
    cover = matcher.minimum_vertex_cover()
    independent = matcher.maximum_independent_set()
    assert cover == sorted(set(cover)) and len(cover) == size
    assert independent == sorted(set(independent))
    assert set(independent) == set(range(n)) - set(cover)
    assert all(u in cover or v in cover for u in range(n) for v in graph[u])
    edge_cover = matcher.minimum_edge_cover()
    if any(not edges for edges in graph):
        assert edge_cover is None
    else:
        assert len(edge_cover) == n - size
        assert {v for edge in edge_cover for v in edge} == set(range(n))
        assert all(v in graph[u] for u, v in edge_cover)
    assert sorted(v for group in matcher.dulmage_mendelsohn() for v in group) == list(range(n))


def test_graph_input_shuffled_disconnected_and_duplicate_edges():
    rng = random.Random(9105)
    for n in range(11):
        for _ in range(60):
            color = [rng.randrange(2) for _ in range(n)]
            graph = [[] for _ in range(n)]
            for u in range(n):
                for v in range(u):
                    if color[u] != color[v] and rng.randrange(3) == 0:
                        for _ in range(1 + (rng.randrange(4) == 0)):
                            graph[u].append(v)
                            graph[v].append(u)
            before = [row[:] for row in graph]
            validate_graph_input(BipartiteMatching(graph), graph)
            assert graph == before


def test_graph_input_dynamic_edges_and_failed_update():
    rng = random.Random(9106)
    for n in range(1, 10):
        color = [rng.randrange(2) for _ in range(n)]
        edges = [(u, v) for u in range(n) for v in range(u) if color[u] != color[v]]
        rng.shuffle(edges)
        graph = [[] for _ in range(n)]
        matcher = BipartiteMatching(graph)
        validate_graph_input(matcher, graph)
        for u, v in edges:
            matcher.add_edge(u, v)
            graph[u].append(v)
            graph[v].append(u)
            validate_graph_input(matcher, graph)
    graph = [[1], [0, 2], [1]]
    matcher = BipartiteMatching(graph)
    for edge in [(0, 2), (1, 1), (-1, 0), (0, 3)]:
        with pytest.raises(ValueError):
            matcher.add_edge(*edge)
        validate_graph_input(matcher, graph)


def test_graph_input_invalid_and_deep():
    for graph in [[[0]], [[1, 2], [0, 2], [0, 1]], [[-1]], [[1]]]:
        with pytest.raises(ValueError):
            BipartiteMatching(graph)
    n = 100000
    graph = [[] for _ in range(n)]
    for v in range(1, n):
        graph[v - 1].append(v)
        graph[v].append(v - 1)
    matcher = BipartiteMatching(graph)
    assert matcher.solve() == n // 2
    assert all(matcher.essential_vertices())


def test_explicit_sides_mates_use_combined_numbering():
    matcher = BipartiteMatching(2, 3)
    matcher.add_edge(1, 2)
    assert matcher.mates() == [-1, 4, -1, -1, 1]


if __name__ == "__main__":
    random.seed(0)
    test_small_against_brute()
    test_edge_cover_and_dynamic_add()
    test_random_against_maxflow()
    test_large_without_recursion()
    test_deep_augmenting_path_without_recursion()
