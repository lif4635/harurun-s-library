import random

from library_codex.combinatorics.BinomialQueries import (
    StirlingNumberQuery,
    comb_prefix_sums,
)
from library_codex.combinatorics.Combination import Comb


def test_comb_prefix_sums():
    rng = random.Random(505)
    queries = []
    for _ in range(5000):
        n = rng.randrange(1000)
        queries.append((n, rng.randrange(n + 1)))
    actual = comb_prefix_sums(queries)
    combination = Comb(1000)
    for value, (n, m) in zip(actual, queries):
        assert value == sum(combination.C(n, k) for k in range(m + 1)) % 998244353


def test_stirling_number_query_against_dp():
    for prime in (2, 3, 5, 7, 11):
        query = StirlingNumberQuery(prime)
        size = 100
        first = [[0] * size for _ in range(size)]
        second = [[0] * size for _ in range(size)]
        first[0][0] = second[0][0] = 1
        for n in range(1, size):
            for k in range(1, n + 1):
                first[n][k] = (first[n - 1][k - 1]
                               - (n - 1) * first[n - 1][k]) % prime
                second[n][k] = (second[n - 1][k - 1]
                                + k * second[n - 1][k]) % prime
        for n in range(size):
            for k in range(n + 1):
                assert query.FirstKind(n, k) == first[n][k]
                assert query.SecondKind(n, k) == second[n][k]
