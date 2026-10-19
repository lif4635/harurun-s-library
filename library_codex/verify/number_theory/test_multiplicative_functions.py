from fractions import Fraction
from math import isqrt
from random import Random

import pytest

from library_codex.number_theory.MultiplicativeFunctions import (
    DirichletQuotientSeries,
    EnumerateMultiplicativePrefixSum,
    MultiplicativePrefixSum,
    dirichlet_divide,
    dirichlet_multiply,
    divisor_count_values,
    divisor_sum_values,
    mobius_values,
    sum_totient_fast,
    totient_values,
)
from library_codex.prime.Sieve import LinearSieve


def _quotient_series(values, n):
    prefix = [Fraction(0)]
    for value in values[1:]:
        prefix.append(prefix[-1] + value)
    series = DirichletQuotientSeries(n)
    for index in range(series.size):
        series[index] = prefix[series.value(index)]
    return series


def test_dirichlet_quotient_multiply_and_divide():
    for n in range(1, 300):
        first_values = [Fraction(0)] + [Fraction(index % 7 - 3)
                                        for index in range(1, n + 1)]
        second_values = [Fraction(0)] + [Fraction(index % 5 + 1)
                                         for index in range(1, n + 1)]
        first = _quotient_series(first_values, n)
        second = _quotient_series(second_values, n)
        product_values = [Fraction(0)] * (n + 1)
        for left in range(1, n + 1):
            for right in range(1, n // left + 1):
                product_values[left * right] += (
                    first_values[left] * second_values[right]
                )
        expected = _quotient_series(product_values, n)
        product = dirichlet_multiply(first, second)
        assert product.data == expected.data
        recovered = dirichlet_divide(product, first)
        assert recovered.data == second.data


def test_multiplicative_value_enumerators():
    for limit in range(1, 300):
        sieve = LinearSieve(limit)
        assert mobius_values(limit) == sieve.mobius
        assert totient_values(limit) == sieve.phi
        divisor_count = divisor_count_values(limit)
        divisor_sum = divisor_sum_values(limit)
        for value in range(1, limit + 1):
            divisors = [d for d in range(1, value + 1) if value % d == 0]
            assert divisor_count[value] == len(divisors)
            assert divisor_sum[value] == sum(divisors)


def test_enumerate_prefix_sum_deconvolution():
    for n in range(1, 1000):
        prefix_divisors = [0] * (n + 1)
        for divisor in range(1, n + 1):
            for multiple in range(divisor, n + 1, divisor):
                prefix_divisors[multiple] += 1
        for index in range(1, n + 1):
            prefix_divisors[index] += prefix_divisors[index - 1]
        enumerator = EnumerateMultiplicativePrefixSum(
            n, lambda x: x, lambda x: prefix_divisors[x]
        )
        left = 1
        while left <= n:
            value = n // left
            assert enumerator(value) == value
            left = n // value + 1


def test_min25_summatory_and_totient_dp():
    for n in range(1, 1000):
        engine = MultiplicativePrefixSum(n)
        prime_count = engine.prime_count_table()
        assert engine.run(prime_count, lambda prime, exponent: 1) == n
        prime_sum = engine.prime_sum_table()
        phi_prime = [left - right for left, right in zip(prime_sum, prime_count)]
        expected = sum(LinearSieve(n).phi[1:])
        assert engine.run(
            phi_prime,
            lambda prime, exponent: prime ** exponent - prime ** (exponent - 1),
        ) == expected
        assert sum_totient_fast(n) == expected


def test_totient_sum_moduli():
    for n in (0, 1, 64, 65, 1000, 10000):
        expected = sum(LinearSieve(n).phi)
        for mod in (1, 2, 6, 998244353):
            assert sum_totient_fast(n, mod) == expected % mod


def test_summatory_random_prime_powers():
    rng = Random(39172)
    for n in [0, 1, 2, 8, 9, 27, 64, 125, 729] + [rng.randrange(2, 3000) for _ in range(30)]:
        sieve = LinearSieve(n)
        values = {}
        for p in sieve.primes:
            power, exponent = p, 1
            while power <= n:
                values[p, exponent] = rng.randrange(-20, 21)
                power *= p
                exponent += 1
        expected = 0
        for x in range(1, n + 1):
            y, value = x, 1
            for p in sieve.primes:
                if p * p > y:
                    break
                exponent = 0
                while y % p == 0:
                    y //= p
                    exponent += 1
                if exponent:
                    value *= values[p, exponent]
            if y > 1:
                value *= values[y, 1]
            expected += value
        for mod in (None, 1, 6, 469762049):
            engine = MultiplicativePrefixSum(n, mod)
            prefix = [0] * engine.size
            cumulative = [0] * (n + 1)
            for p in sieve.primes:
                cumulative[p] = values[p, 1]
            for x in range(1, n + 1):
                cumulative[x] += cumulative[x - 1]
            for x in range(1, n + 1):
                if n // (n // x) == x:
                    prefix[engine.index(x)] = cumulative[x]
            before = prefix[:]
            result = expected if mod is None else expected % mod
            assert engine.run(prefix, lambda p, e: values[p, e]) == result
            assert engine.run(prefix, lambda p, e: values[p, e]) == result
            assert prefix == before


def test_summatory_fraction_and_invalid_table():
    engine = MultiplicativePrefixSum(100)
    prefix = [Fraction(x, 2) for x in engine.prime_count_table()]
    primes = LinearSieve(100).primes
    expected = sum(Fraction(1, 2) ** sum(x % p == 0 for p in primes) for x in range(1, 101))
    assert engine.run(prefix, lambda p, e: Fraction(1, 2)) == expected
    with pytest.raises(ValueError, match="wrong size"):
        engine.run([], lambda p, e: 1)

