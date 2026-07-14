from math import isqrt

from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD
from library_codex.math.Combinatorics import Combination


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
    inverse_two = pow(2, -1, mod)
    current_n = 0
    current_m = 0
    current = 1
    result = [0] * len(queries)
    for query_index in order:
        target_n, target_m = queries[query_index]
        while current_m > target_m:
            current = (current - combination.binomial(
                current_n, current_m
            )) % mod
            current_m -= 1
        while current_n < target_n:
            current = (current + current
                       - combination.binomial(current_n, current_m)) % mod
            current_n += 1
        while current_n > target_n:
            current_n -= 1
            current = ((current + combination.binomial(
                current_n, current_m
            )) * inverse_two) % mod
        while current_m < target_m:
            current_m += 1
            current = (current + combination.binomial(
                current_n, current_m
            )) % mod
        result[query_index] = current
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
