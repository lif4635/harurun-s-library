from itertools import product
from math import inf
import random

import pytest

from library_codex.optimization.ProjectSelection import (
    KProjectSelection,
    ProjectSelection,
)


def binary_cost(unary, pairs, assignment):
    return sum(unary[i][assignment[i]] for i in range(len(unary))) + sum(
        costs[assignment[first]][assignment[second]]
        for first, second, costs in pairs
    )


def binary_brute(unary, pairs):
    return min(
        binary_cost(unary, pairs, assignment)
        for assignment in product(range(2), repeat=len(unary))
    )


def test_binary_project_selection_against_brute():
    rng = random.Random(519873)
    for size in range(8):
        for _ in range(1000):
            unary = [[rng.randrange(-20, 21) for _ in range(2)] for _ in range(size)]
            pairs = []
            solver = ProjectSelection(size)
            for variable in range(size):
                solver.add_unary_cost(variable, *unary[variable])
            for first in range(size):
                for second in range(first):
                    if rng.randrange(3) == 0:
                        a = rng.randrange(-20, 21)
                        b = rng.randrange(-20, 21)
                        c = rng.randrange(-20, 21)
                        d = b + c - a - rng.randrange(21)
                        costs = [[a, b], [c, d]]
                        pairs.append((first, second, costs))
                        solver.add_pair_cost(first, second, costs)
            expected = binary_brute(unary, pairs)
            value, assignment = solver.min_cost()
            assert value == expected
            assert binary_cost(unary, pairs, assignment) == expected


def test_project_selection_combines_signed_pair_terms_at_build():
    unary = [[-8, 3], [4, -5]]
    costs = [[2, 7], [-3, 1]]
    solver = ProjectSelection(2)
    solver.add_unary_cost(0, *unary[0])
    solver.add_unary_cost(1, *unary[1])
    solver.add_cost_01(0, 1, -7)
    solver.add_pair_cost(0, 1, [[2, 14], [-3, 1]])
    value, assignment = solver.min_cost()
    assert value == binary_brute(unary, [(0, 1, costs)])
    assert value == binary_cost(unary, [(0, 1, costs)], assignment)


def test_project_selection_build_rejects_only_invalid_combined_table():
    solver = ProjectSelection(2)
    solver.add_cost_01(0, 1, -3)
    with pytest.raises(ValueError, match="not submodular"):
        solver.build()
    solver.add_cost_01(0, 1, 5)
    graph, offset = solver.build()
    assert offset == 0
    assert all(0 <= edge[2] < inf for edge in graph.edges())


def test_project_selection_random_signed_pair_aggregation():
    rng = random.Random(185927)
    for _ in range(500):
        size = rng.randrange(1, 6)
        solver = ProjectSelection(size)
        unary = [[rng.randrange(-20, 21) for _ in range(2)] for _ in range(size)]
        for variable, costs in enumerate(unary):
            solver.add_unary_cost(variable, *costs)
        pairs = []
        for first in range(size):
            for second in range(first):
                if rng.randrange(2):
                    target = [rng.randrange(-30, 31) for _ in range(3)]
                    target.append(
                        target[1] + target[2] - target[0] - rng.randrange(20)
                    )
                    split = [rng.randrange(-50, 51) for _ in range(4)]
                    solver.add_pair_cost(first, second, [split[:2], split[2:]])
                    remainder = [target[i] - split[i] for i in range(4)]
                    solver.add_pair_cost(
                        second,
                        first,
                        [[remainder[0], remainder[2]], [remainder[1], remainder[3]]],
                    )
                    pairs.append((first, second, [target[:2], target[2:]]))
        expected = binary_brute(unary, pairs)
        value, assignment = solver.min_cost()
        assert value == expected
        assert binary_cost(unary, pairs, assignment) == expected


def test_project_selection_infinite_costs_are_hard_constraints():
    solver = ProjectSelection(3)
    solver.add_unary_cost(0, inf, -10**30)
    solver.add_pair_cost(0, 1, [[0, 0], [inf, 0]])
    solver.add_pair_cost(1, 2, [[0, 0], [inf, 0]])
    solver.add_unary_cost(2, -10**30, 0)
    value, assignment = solver.min_cost()
    assert assignment == [1, 1, 1]
    assert value == -10**30

    forced_row = ProjectSelection(2)
    forced_row.add_pair_cost(0, 1, [[inf, inf], [0, 7]])
    value, assignment = forced_row.min_cost()
    assert value == 0
    assert assignment == [1, 0]

    impossible = ProjectSelection(1)
    impossible.add_unary_cost(0, inf, inf)
    with pytest.raises(ValueError, match="forbid every"):
        impossible.min_cost()


def test_project_selection_manual_build():
    solver = ProjectSelection(2)
    solver.add_unary_cost(0, 7, -2)
    solver.add_cost_10(0, 1, 11)
    graph, offset = solver.build()
    value = offset + graph.flow(solver.source, solver.sink)
    reachable = graph.min_cut(solver.source)
    assignment = [0 if reachable[variable] else 1 for variable in range(2)]
    assert value == -2
    assert assignment == [1, 1]


def test_k_project_selection_against_brute_monge():
    rng = random.Random(613894)
    for _ in range(5000):
        sizes = [rng.randrange(1, 5) for _ in range(rng.randrange(1, 5))]
        solver = KProjectSelection(sizes)
        unary = []
        for variable, size in enumerate(sizes):
            costs = [rng.randrange(-20, 21) for _ in range(size)]
            unary.append(costs)
            solver.add_unary_cost(variable, costs)
        pairs = []
        for first in range(len(sizes)):
            for second in range(first):
                if rng.randrange(2):
                    left = [rng.randrange(-10, 11) for _ in range(sizes[first])]
                    right = [rng.randrange(-10, 11) for _ in range(sizes[second])]
                    weight = rng.randrange(10)
                    costs = [
                        [left[x] + right[y] - weight * x * y for y in range(sizes[second])]
                        for x in range(sizes[first])
                    ]
                    pairs.append((first, second, costs))
                    solver.add_pair_cost(first, second, costs)
        expected = min(
            sum(unary[i][assignment[i]] for i in range(len(sizes)))
            + sum(
                costs[assignment[first]][assignment[second]]
                for first, second, costs in pairs
            )
            for assignment in product(*(range(size) for size in sizes))
        )
        value, assignment = solver.min_cost()
        assert value == expected
        actual = sum(unary[i][assignment[i]] for i in range(len(sizes)))
        actual += sum(
            costs[assignment[i]][assignment[j]]
            for i, j, costs in pairs
        )
        assert actual == expected
