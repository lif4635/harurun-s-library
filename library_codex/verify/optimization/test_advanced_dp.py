import random

from library_codex.optimization.AdvancedDP import (
    RollbackMo,
    concave_max_plus_convolution,
    convex_min_plus_convolution,
    enumerate_monge_d_edge_shortest_paths,
    knapsack_branch_and_bound,
    monge_d_edge_shortest_path,
    monge_shortest_paths,
)


def test_convex_and_concave_convolution_against_quadratic():
    rng = random.Random(61)
    for _ in range(300):
        n = rng.randrange(1, 30)
        m = rng.randrange(1, 30)
        differences = sorted(rng.randrange(-20, 21) for _ in range(n - 1))
        convex = [rng.randrange(-30, 31)]
        for difference in differences:
            convex.append(convex[-1] + difference)
        arbitrary = [rng.randrange(-100, 101) for _ in range(m)]
        expected = [min(convex[i] + arbitrary[k - i]
                        for i in range(n) if 0 <= k - i < m)
                    for k in range(n + m - 1)]
        values, indices = convex_min_plus_convolution(convex, arbitrary, True)
        assert values == expected
        assert all(convex[index] + arbitrary[k - index] == values[k]
                   for k, index in enumerate(indices))
        concave = [-value for value in convex]
        expected = [max(concave[i] + arbitrary[k - i]
                        for i in range(n) if 0 <= k - i < m)
                    for k in range(n + m - 1)]
        assert concave_max_plus_convolution(concave, arbitrary) == expected


def test_monge_shortest_paths_against_dynamic_programming():
    rng = random.Random(62)
    for target in range(1, 70):
        bias = [rng.randrange(-20, 21) for _ in range(target + 1)]

        def cost(first, second):
            return (second - first) ** 2 + bias[second]

        brute = [10 ** 100] * (target + 1)
        brute[0] = 0
        for second in range(1, target + 1):
            brute[second] = min(brute[first] + cost(first, second)
                                for first in range(second))
        assert monge_shortest_paths(target, cost) == brute
        exact = [10 ** 100] * (target + 1)
        previous = [10 ** 100] * (target + 1)
        previous[0] = 0
        for edges in range(1, target + 1):
            current = [10 ** 100] * (target + 1)
            for second in range(1, target + 1):
                current[second] = min(
                    (previous[first] + cost(first, second)
                     for first in range(second)), default=10 ** 100
                )
            previous = current
            exact[edges] = current[target]
        assert enumerate_monge_d_edge_shortest_paths(target, cost) == exact
        for edges in {1, (target + 1) // 2, target}:
            assert monge_d_edge_shortest_path(target, edges, cost) == exact[edges]


def test_knapsack_branch_bound_against_subsets():
    rng = random.Random(63)
    for size in range(18):
        for _ in range(20):
            values = [rng.randrange(-5, 50) for _ in range(size)]
            weights = [rng.randrange(0, 30) for _ in range(size)]
            capacity = rng.randrange(60)
            expected = 0
            for mask in range(1 << size):
                weight = value = 0
                for index in range(size):
                    if mask >> index & 1:
                        weight += weights[index]
                        value += values[index]
                if weight <= capacity and value > expected:
                    expected = value
            assert knapsack_branch_and_bound(values, weights, capacity) == expected


def test_rollback_mo_range_sums():
    rng = random.Random(64)
    values = [rng.randrange(-100, 101) for _ in range(300)]
    queries = [(rng.randrange(301), rng.randrange(301)) for _ in range(1000)]
    queries = [(min(left, right), max(left, right)) for left, right in queries]
    mo = RollbackMo(len(values))
    for query in queries:
        mo.add(*query)
    state = [0]
    snapshots = []

    def initialize():
        state[0] = 0
        snapshots.clear()

    def insert(index):
        state[0] += values[index]

    def snapshot():
        snapshots.append(state[0])

    def rollback():
        state[0] = snapshots[-1]

    answers = mo.run(initialize, insert, snapshot, rollback,
                     lambda _query: state[0])
    assert answers == [sum(values[left:right]) for left, right in queries]
