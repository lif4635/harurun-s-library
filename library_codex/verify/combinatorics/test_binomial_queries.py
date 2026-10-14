import random

from library_codex.combinatorics.BinomialQueries import comb_prefix_sums
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
