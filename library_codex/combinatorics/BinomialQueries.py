"""二項係数の部分和を、隣接する添字への移動や一括queryで求める。"""

from math import isqrt

from library_codex.fps.FormalPowerSeries import DEFAULT_MOD
from library_codex.combinatorics.Combination import Comb


class BinomialPrefix:
    """sum(C(n,k), 0 <= k <= m)を隣接する(n,m)へO(1)で動かす。"""

    __slots__ = ("combination", "inverse_two", "n", "m", "value")

    def __init__(self, combination):
        self.combination = combination
        self.inverse_two = pow(2, -1, combination.mod)
        self.n = self.m = 0
        self.value = 1

    def move(self, n, m):
        """現在位置から(n,m)へ移動し、sum(C(n,k), 0<=k<=m)を返す。O(|Δn|+|Δm|)。"""
        if n < 0 or not 0 <= m <= n:
            raise ValueError("move requires 0 <= m <= n")
        combination = self.combination
        mod = combination.mod
        while self.m > m:
            self.value = (self.value - combination.C(self.n, self.m)) % mod
            self.m -= 1
        while self.n < n:
            self.value = (2 * self.value - combination.C(self.n, self.m)) % mod
            self.n += 1
        while self.n > n:
            self.n -= 1
            self.value = ((self.value + combination.C(self.n, self.m))
                          * self.inverse_two % mod)
        while self.m < m:
            self.m += 1
            self.value = (self.value + combination.C(self.n, self.m)) % mod
        return self.value

    def get(self):
        """現在位置の二項係数prefix和を返す。O(1)。"""
        return self.value


def comb_prefix_sums(queries, mod=DEFAULT_MOD):
    """For every (n,m), return sum(C(n,k), 0 <= k <= m)."""
    if not queries:
        return []
    maximum = 0
    for n, m in queries:
        if n < 0 or not 0 <= m <= n:
            raise ValueError("queries require 0 <= m <= n")
        maximum = max(maximum, n)
    combination = Comb(maximum, mod)
    block = max(1, isqrt(maximum + 1))
    order = list(range(len(queries)))
    order.sort(key=lambda index: (
        queries[index][0] // block,
        queries[index][1] if (queries[index][0] // block) & 1 == 0
        else -queries[index][1],
    ))
    cursor = BinomialPrefix(combination)
    result = [0] * len(queries)
    for query_index in order:
        target_n, target_m = queries[query_index]
        result[query_index] = cursor.move(target_n, target_m)
    return result
