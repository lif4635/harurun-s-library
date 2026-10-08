import random

import pytest

from library_codex.graph_spanning.MinimumSteinerTree import minimum_steiner_tree, steiner_tree_dp


def _connected_terminals(n, edges, selected, terminals):
    if not terminals:
        return True
    graph = [[] for _ in range(n)]
    for edge_id in selected:
        u, v, _ = edges[edge_id]
        graph[u].append(v)
        graph[v].append(u)
    seen = {terminals[0]}
    stack = [terminals[0]]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return all(v in seen for v in terminals)


def test_minimum_steiner_tree_against_edge_subsets():
    rng = random.Random(11)
    for n in range(2, 8):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(100):
            rng.shuffle(pairs)
            chosen_pairs = pairs[:rng.randrange(min(len(pairs), 8) + 1)]
            edges = [(u, v, rng.randrange(7)) for u, v in chosen_pairs]
            terminals = rng.sample(range(n), rng.randrange(1, min(4, n) + 1))
            expected = float("inf")
            for mask in range(1 << len(edges)):
                selected = [i for i in range(len(edges)) if mask >> i & 1]
                if _connected_terminals(n, edges, selected, terminals):
                    expected = min(expected, sum(edges[i][2] for i in selected))
            value, selected = minimum_steiner_tree(n, edges, terminals)
            assert value == expected
            if value < float("inf"):
                assert _connected_terminals(n, edges, selected, terminals)
                assert sum(edges[i][2] for i in selected) == value
            table = steiner_tree_dp(n, edges, terminals)
            assert min(table[-1]) == expected


def test_steiner_root_choice_zero_parallel_and_large_weights():
    import itertools

    edges = [(0, 1, 0), (0, 1, 5), (1, 2, 0), (2, 3, 10**40), (1, 3, 10**40 + 1)]
    for terminals in itertools.permutations([0, 2, 3]):
        value, selected = minimum_steiner_tree(4, iter(edges), terminals + terminals)
        assert value == 10**40
        assert len(selected) == len(set(selected))
        assert sum(edges[i][2] for i in selected) == value
        assert _connected_terminals(4, edges, selected, terminals)
    assert minimum_steiner_tree(0, [], []) == (0, [])
    assert minimum_steiner_tree(2, [], [1, 1]) == (0, [])
    assert minimum_steiner_tree(2, [], [0, 1]) == (float('inf'), [])
    with pytest.raises(ValueError):
        minimum_steiner_tree(2, [(0, 1, -1)], [0, 1])
    with pytest.raises(IndexError):
        minimum_steiner_tree(2, [], [2])


def test_steiner_table_all_terminal_subsets():
    edges = [(0, 1, 2), (1, 2, 1), (1, 3, 3), (2, 3, 5)]
    terminals = [0, 2, 3]
    before = edges[:], terminals[:]
    table = steiner_tree_dp(4, edges, terminals)
    for mask in range(1, 8):
        selected = [terminals[i] for i in range(3) if mask >> i & 1]
        for v in range(4):
            assert table[mask][v] == minimum_steiner_tree(4, edges, selected + [v])[0]
    assert (edges, terminals) == before
