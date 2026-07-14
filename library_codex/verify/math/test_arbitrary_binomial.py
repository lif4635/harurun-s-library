from math import comb

from library_codex.math.ArbitraryBinomial import (
    ArbitraryModBinomial,
    LargePrimeFactorial,
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
            assert factorial.fact(value) == expected
    query = ArbitraryModBinomial(prime)
    for n, k in ((10 ** 18 + 123, 7), (prime + 100, 50),
                 (2 * prime + 91, prime + 12)):
        # Independent digit-wise Lucas with small digit binomials.
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

