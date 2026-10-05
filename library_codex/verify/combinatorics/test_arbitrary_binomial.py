from math import comb

from library_codex.combinatorics.ArbitraryBinomial import (
    ArbitraryModBinomial,
    LargePrimeFactorial,
    PrimePowerBinomial,
)


def test_arbitrary_mod_binomial_exhaustive_small():
    for mod in range(1, 180):
        query = ArbitraryModBinomial(mod)
        for n in range(70):
            for k in range(n + 1):
                assert query.C(n, k) == comb(n, k) % mod


def test_large_prime_factorial_and_lucas():
    prime = 1_000_003
    factorial = LargePrimeFactorial(prime)
    expected = 1
    for value in range(1, 10001):
        expected = expected * value % prime
        if value in (2, 10, 99, 1000, 10000):
            assert factorial.factorial(value) == expected
    query = ArbitraryModBinomial(prime)
    for n, k in ((10 ** 18 + 123, 7), (prime + 100, 50),
                 (2 * prime + 91, prime + 12)):
        a, b = n, k
        expected = 1
        while a:
            a, ad = divmod(a, prime)
            b, bd = divmod(b, prime)
            if ad < bd:
                expected = 0
                break
            expected = expected * (comb(ad, bd) % prime) % prime
        assert query.C(n, k) == expected


def test_prime_power_growth_and_large_sparse_queries():
    for prime, exponent in [(2, 8), (3, 4), (5, 3), (7, 2)]:
        table = PrimePowerBinomial(prime, exponent)
        for n in [1, 7, 3, 25, 100, 200, 1000, 1200]:
            for k in [0, 1, 2, 7, n // 2, n, n + 1, -1]:
                expected = comb(n, k) % table.mod if 0 <= k <= n else 0
                assert table.C(n, k) == expected
        for a, b in zip(table.prefix, table.inverse_prefix):
            assert a * b % table.mod == 1
    prime = 1000000007
    table = PrimePowerBinomial(prime, 1)
    assert table.C(prime, 1) == 0
    assert table.C(prime, prime) == 1
    assert table.C(prime + 1, 1) == 1
    assert len(table.prefix) < 10


def test_invalid_binomial_inputs():
    import pytest

    for args in [(1, 2), (2, 0), (3, -1)]:
        with pytest.raises(ValueError):
            PrimePowerBinomial(*args)
    for mod in [1, 8, 35, 1000000007]:
        table = ArbitraryModBinomial(mod)
        assert table.C(-1, 0) == table.C(1, -1) == table.C(1, 2) == 0
