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


def test_dirichlet_random_modular_and_sparse():
    rng = Random(62891)
    bounds = [1, 2, 3, 7, 8, 9, 26, 27, 28, 63, 64, 65, 999, 1000, 1001, 4096]
    bounds += [rng.randrange(1, 500) for _ in range(30)]
    for mod in (1, 6, 998244353, 2**70 + 33):
        for n in bounds:
            a = [0] + [rng.randrange(-20, 21) if rng.randrange(3) else 0 for _ in range(n)]
            b = [0] + [rng.randrange(-20, 21) if rng.randrange(3) else 0 for _ in range(n)]
            a[1] = -1
            c = [0] * (n + 1)
            for x in range(1, n + 1):
                for y in range(1, n // x + 1):
                    c[x * y] += a[x] * b[y]
            tables = []
            for values in (a, b, c):
                prefix = [0]
                for value in values[1:]:
                    prefix.append((prefix[-1] + value) % mod)
                series = DirichletQuotientSeries(n, mod=mod)
                series.data = [prefix[series.value(i)] for i in range(series.size)]
                tables.append(series)
            first, second, expected = tables
            snapshots = [s.data[:] for s in tables]
            assert dirichlet_multiply(first, second).data == expected.data
            assert dirichlet_multiply(second, first).data == expected.data
            assert dirichlet_divide(expected, first).data == second.data
            assert [s.data for s in tables] == snapshots


def test_dirichlet_identity_and_invalid_parameters():
    n = 10000
    a = DirichletQuotientSeries(n, mod=998244353)
    a.data = [0] + [i * 711 for i in range(1, a.size)]
    unit = DirichletQuotientSeries(n, [0] + [1] * (a.size - 1), a.mod)
    zero = DirichletQuotientSeries(n, mod=a.mod)
    assert dirichlet_multiply(a, unit).data == a.data
    assert dirichlet_multiply(a, zero).data == zero.data
    assert dirichlet_divide(a, unit).data == a.data
    assert dirichlet_divide(a, a).data == unit.data
    for function in (dirichlet_multiply, dirichlet_divide):
        with pytest.raises(ValueError, match="parameters"):
            function(a, DirichletQuotientSeries(n - 1, mod=a.mod))
        with pytest.raises(ValueError, match="parameters"):
            function(a, DirichletQuotientSeries(n, mod=6))
    with pytest.raises(ValueError):
        dirichlet_divide(DirichletQuotientSeries(1, [0, 1], 6), DirichletQuotientSeries(1, [0, 2], 6))


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


def test_prime_tables_all_quotients():
    rng = Random(683219)
    limits = list(range(50)) + [9999, 10000, 10001, 49999, 50000]
    limits += [rng.randrange(50, 5000) for _ in range(20)]
    for n in limits:
        sieve = LinearSieve(n)
        counts, sums = [0] * (n + 1), [0] * (n + 1)
        for p in sieve.primes:
            counts[p], sums[p] = 1, p
        for x in range(1, n + 1):
            counts[x] += counts[x - 1]
            sums[x] += sums[x - 1]
        for mod in (None, 1, 2, 6, 469762049, 2**70 + 33):
            engine = MultiplicativePrefixSum(n, mod)
            actual_counts = engine.prime_count_table()
            actual_sums = engine.prime_sum_table()
            assert len(actual_counts) == len(actual_sums) == engine.size
            for x in {n // i for i in range(1, n + 1)}:
                assert actual_counts[engine.index(x)] == counts[x]
                assert actual_sums[engine.index(x)] == (sums[x] if mod is None else sums[x] % mod)
            assert engine.prime_sum_table() == actual_sums


def test_bounded_integer_division():
    from library_codex.number_theory.MultiplicativeFunctions import _small_quotient

    rng = Random(7312)
    bound = 2**50
    for d in [1, 2, 3, 5, 7, 998244353, bound - 1, bound, bound + 1, 2**80] + [rng.randrange(1, bound) for _ in range(10000)]:
        for n in (0, 1, bound - 1, bound, bound + 1, 2**80 + 3):
            assert _small_quotient(n, d) == n // d
        q = rng.randrange(bound // d + 1)
        for n in (max(0, q * d - 1), q * d, q * d + 1):
            assert _small_quotient(n, d) == n // d


def test_summatory_large_residues_and_exact_arithmetic():
    for n in (100, 999, 10000):
        sieve = LinearSieve(n)
        for mod in (469762049, 2**70 + 33):
            a, b = mod - 3, mod - 7
            values = [1] * (n + 1)
            for p in sieve.primes:
                for x in range(p, n + 1, p):
                    y, e = x, 0
                    while y % p == 0:
                        y //= p
                        e += 1
                    values[x] = values[x] * (a * e + b * p) % mod
            engine = MultiplicativePrefixSum(n, mod)
            prefix = [(a * x + b * y) % mod for x, y in zip(engine.prime_count_table(), engine.prime_sum_table())]
            assert engine.run(prefix, lambda p, e: (a * e + b * p) % mod) == sum(values[1:]) % mod

