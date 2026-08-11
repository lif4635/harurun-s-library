import itertools
import random

from library_codex.graph.TournamentPath import tournament_hamiltonian_path
from library_codex.graph.TwoSAT import TwoSAT
from library_codex.graph_flow.MaxFlow import (
    feasible_circulation,
    max_flow_with_bounds,
)
from library_codex.graph_spanning.MinimumSpanningTree import second_spanning_tree
from library_codex.tree.TreeDiameter import tree_metric_center


def test_two_sat_at_most_one():
    solver = TwoSAT(5)
    literals = [solver.literal(i) for i in range(5)]
    solver.add_at_most_one(literals)
    solver.set_value(3)
    answer = solver.solve()
    assert answer is not None and answer[3]
    assert sum(answer) == 1
    solver = TwoSAT(2)
    solver.add_at_most_one([solver.literal(0), solver.literal(1)])
    solver.set_value(0)
    solver.set_value(1)
    assert solver.solve() is None


def _all_spanning_tree_costs(n, edges):
    result = []
    for chosen in itertools.combinations(range(len(edges)), n - 1):
        parent = list(range(n))
        def find(v):
            while parent[v] != v:
                v = parent[v]
            return v
        for edge_id in chosen:
            first, second, _ = edges[edge_id]
            first, second = find(first), find(second)
            if first != second:
                parent[second] = first
        if len({find(v) for v in range(n)}) == 1:
            result.append((sum(edges[i][2] for i in chosen), tuple(chosen)))
    return sorted(result)


def test_second_spanning_tree_random_against_enumeration():
    random.seed(20260824)
    for n in range(2, 8):
        for _ in range(120):
            edges = [(i, i + 1, random.randrange(1, 7)) for i in range(n - 1)]
            for i in range(n):
                for j in range(i + 2, n):
                    if random.randrange(2):
                        edges.append((i, j, random.randrange(1, 7)))
            all_trees = _all_spanning_tree_costs(n, edges)
            got = second_spanning_tree(n, edges)
            if len(all_trees) < 2:
                assert got is None
            else:
                assert got is not None
                mst_cost, second_cost, mst_edges, second_edges, added, removed = got
                assert mst_cost == all_trees[0][0]
                expected = min(cost for cost, chosen in all_trees
                               if set(chosen) != set(mst_edges))
                assert second_cost == expected
                assert set(second_edges) == set(mst_edges) - {removed} | {added}
            strict = second_spanning_tree(n, edges, strict=True)
            larger = [cost for cost, _ in all_trees if cost > all_trees[0][0]]
            assert (None if not larger else strict[1]) == (
                None if not larger else min(larger)
            )


def test_tournament_hamiltonian_path_random():
    random.seed(20260825)
    for n in range(50):
        graph = [[] for _ in range(n)]
        for first in range(n):
            for second in range(first + 1, n):
                if random.randrange(2):
                    graph[first].append(second)
                else:
                    graph[second].append(first)
        path = tournament_hamiltonian_path(graph)
        assert sorted(path) == list(range(n))
        assert all(path[i + 1] in graph[path[i]] for i in range(n - 1))


def test_flow_with_bounds_and_circulation():
    circulation = [(0, 1, 1, 3), (1, 2, 1, 2), (2, 0, 1, 4)]
    flows = feasible_circulation(3, circulation)
    assert flows is not None
    balance = [0, 0, 0]
    for flow, (first, second, lower, upper) in zip(flows, circulation):
        assert lower <= flow <= upper
        balance[first] -= flow
        balance[second] += flow
    assert balance == [0, 0, 0]

    edges = [(0, 1, 1, 4), (0, 2, 0, 3), (1, 2, 0, 2),
             (1, 3, 1, 3), (2, 3, 1, 5)]
    value, flows = max_flow_with_bounds(4, edges, 0, 3)
    brute = []
    for candidate in itertools.product(*[range(low, high + 1)
                                         for _, _, low, high in edges]):
        balance = [0] * 4
        for flow, (first, second, _, _) in zip(candidate, edges):
            balance[first] -= flow
            balance[second] += flow
        if balance[1] == balance[2] == 0 and balance[0] == -balance[3]:
            brute.append(balance[3])
    assert value == max(brute)


def test_weighted_tree_metric_center_vertex_and_edge():
    tree = [[(1, 2)], [(0, 2), (2, 4)], [(1, 4)]]
    assert tree_metric_center(tree) == (3, (1, 2, 1))
    unweighted = [[1], [0, 2], [1, 3], [2]]
    assert tree_metric_center(unweighted) == (1.5, (1, 2, 0.5))
