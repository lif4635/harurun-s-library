from math import isqrt

from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD
from library_codex.math.Combination import Combination


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


def multipoint_binomial_prefix_sum(queries, mod=DEFAULT_MOD):
    """For every (n,m), return sum(C(n,k), 0 <= k <= m)."""
    if not queries:
        return []
    maximum = 0
    for n, m in queries:
        if n < 0 or not 0 <= m <= n:
            raise ValueError("queries require 0 <= m <= n")
        maximum = max(maximum, n)
    combination = Combination(maximum, mod)
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


class StirlingNumberQuery:
    __slots__ = ("prime", "binomial_table", "first", "second")

    def __init__(self, prime):
        if prime < 2:
            raise ValueError("prime must be at least two")
        self.prime = prime
        binomial = [[0] * prime for _ in range(prime)]
        first = [[0] * prime for _ in range(prime)]
        second = [[0] * prime for _ in range(prime)]
        binomial[0][0] = first[0][0] = second[0][0] = 1
        for n in range(1, prime):
            for k in range(n + 1):
                if k:
                    binomial[n][k] = binomial[n - 1][k - 1]
                    first[n][k] = first[n - 1][k - 1]
                    second[n][k] = second[n - 1][k - 1]
                binomial[n][k] = (binomial[n][k]
                                  + binomial[n - 1][k]) % prime
                first[n][k] = (first[n][k]
                               + (prime - n + 1) * first[n - 1][k]) % prime
                second[n][k] = (second[n][k]
                                + k * second[n - 1][k]) % prime
        self.binomial_table = binomial
        self.first = first
        self.second = second

    def _binomial(self, n, k):
        if n < 0 or k < 0 or n < k:
            return 0
        result = 1
        prime = self.prime
        while n:
            n, nd = divmod(n, prime)
            k, kd = divmod(k, prime)
            if kd > nd:
                return 0
            result = result * self.binomial_table[nd][kd] % prime
        return result

    def first_kind(self, n, k):
        if n < 0 or k < 0 or k > n:
            return 0
        prime = self.prime
        quotient, remainder = divmod(n, prime)
        if k < quotient:
            return 0
        a, b = divmod(k - quotient, prime - 1)
        if b == 0 and remainder:
            b += prime - 1
            a -= 1
        if a < 0 or a > quotient or b > remainder:
            return 0
        result = self._binomial(quotient, a) * self.first[remainder][b] % prime
        return -result % prime if (quotient + a) & 1 else result

    FirstKind = first_kind

    def second_kind(self, n, k):
        if n < 0 or k < 0 or k > n:
            return 0
        if n == 0:
            return 1
        prime = self.prime
        quotient, remainder = divmod(k, prime)
        if n < quotient:
            return 0
        a, b = divmod(n - quotient, prime - 1)
        if b == 0:
            b += prime - 1
            a -= 1
        if a < 0 or b < remainder:
            return 0
        if b == prime - 1 and remainder == 0:
            return self._binomial(a, quotient - 1)
        return self._binomial(a, quotient) * self.second[b][remainder] % prime

    SecondKind = second_kind


multipoint_binomial_sum = multipoint_binomial_prefix_sum
