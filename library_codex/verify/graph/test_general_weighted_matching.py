import random

from library_codex.graph.GeneralWeightedMatching import GeneralWeightedMatching


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

