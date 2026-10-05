import random

from library_codex.graph_matching.GeneralWeightedMatching import GeneralWeightedMatching


def _brute(weights):
    n = len(weights)
    dp = [0] * (1 << n)
    for mask in range(1, 1 << n):
        first_bit = mask & -mask
        first = first_bit.bit_length() - 1
        without = mask ^ first_bit
        best = dp[without]
        rest = without
        while rest:
            bit = rest & -rest
            second = bit.bit_length() - 1
            best = max(best, weights[first][second] + dp[without ^ bit])
            rest ^= bit
        dp[mask] = best
    return dp[-1]


def test_general_weighted_matching_against_subset_dp():
    rng = random.Random(333)
    for n in range(1, 12):
        for _ in range(100):
            weights = [[0] * n for _ in range(n)]
            matching = GeneralWeightedMatching(n)
            for first in range(n):
                for second in range(first + 1, n):
                    if rng.randrange(4):
                        weight = rng.randrange(1, 1000)
                        weights[first][second] = weights[second][first] = weight
                        matching.add_edge(first, second, weight)
            mate = matching.run()
            score = 0
            for vertex, other in enumerate(mate):
                if other >= 0:
                    assert mate[other] == vertex
                    if vertex < other:
                        score += weights[vertex][other]
            assert score == _brute(weights)


def test_empty_parallel_and_nonpositive_edges():
    assert GeneralWeightedMatching(0).run() == []
    assert GeneralWeightedMatching(5).run() == [-1] * 5
    matching = GeneralWeightedMatching(5)
    for u, v, w in [(0, 0, 100), (0, 1, 3), (1, 0, 8), (0, 1, 2),
                    (1, 2, -9), (2, 3, 0), (3, 4, 7)]:
        matching.add_edge(u, v, w)
    assert matching.run() == [1, 0, -1, 4, 3]
    assert matching.run() == [1, 0, -1, 4, 3]

