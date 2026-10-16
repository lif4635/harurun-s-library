import math
from bisect import bisect_right
import random
import pytest

from library_codex.prime.Sieve import LinearSieve, prime_sieve, enumerate_primes, prime_count, count_square_free
from library_codex.prime.Sieve import sum_totient


def _is_prime(value):
    return value >= 2 and all(value % divisor
                              for divisor in range(2, math.isqrt(value) + 1))


def test_linear_sieve_prime_count_and_square_free():
    sieve = LinearSieve(100_000)
    assert all(_is_prime(value) for value in sieve.primes)
    assert len(sieve.primes) == 9592
    for value in range(1, 100_001):
        factors = sieve.factor_count(value)
        product = 1
        for prime, exponent in factors:
            product *= prime ** exponent
        assert product == value
        expected_phi = value
        for prime, _ in factors:
            expected_phi -= expected_phi // prime
        assert sieve.phi[value] == expected_phi
        square_free = all(exponent == 1 for _, exponent in factors)
        assert sieve.mobius[value] == (
            (-1) ** len(factors) if square_free else 0
        )
    primes = prime_sieve(1_000_000)
    for number in list(range(10_000)) + [10**5, 10**6, 10**7, 10**8]:
        expected = bisect_right(primes, number)
        if number > 1_000_000:
            expected = {10**7: 664579, 10**8: 5761455}[number]
        assert prime_count(number) == expected
    square_free_prefix = [0] * 2_001
    for value in range(1, 2_001):
        square_free_prefix[value] = square_free_prefix[value - 1] + int(
            all(exponent == 1 for _, exponent in sieve.factor_count(value))
        )
    for number in range(2_001):
        assert count_square_free(number) == square_free_prefix[number]


def test_enumeration_sampling_and_boundaries():
    rng = random.Random(218)
    for limit in list(range(120)) + [524287, 524288, 524289, 524290, 1048579]:
        expected = LinearSieve(limit).primes
        assert prime_sieve(limit) == expected
        for _ in range(6):
            step = rng.randrange(1, 200)
            offset = rng.randrange(step)
            assert enumerate_primes(limit, step, offset) == (len(expected), expected[offset::step])
    assert enumerate_primes(10000000, 10000000, 0) == (664579, [2])
    assert enumerate_primes(100, 1000, 999) == (25, [])
    for args in [(-1,), (10, 0), (10, 3, -1), (10, 3, 3)]:
        with pytest.raises(ValueError):
            enumerate_primes(*args)


def test_totient_sum_against_linear_sieve():
    rng = random.Random(222)
    expected = LinearSieve(200000).phi
    for i in range(1, len(expected)):
        expected[i] += expected[i - 1]
    limits = list(range(300)) + [rng.randrange(len(expected)) for _ in range(60)]
    limits += [n**3 + offset for n in range(5, 40) for offset in (-1, 0, 1)]
    for limit in limits:
        assert sum_totient(limit) == expected[limit]
        mod = rng.choice([1, 2, 6, 17, 998244353, 10**30 + 7])
        assert sum_totient(limit, mod) == expected[limit] % mod
    assert sum_totient(-1) == sum_totient(0) == 0
    for mod in (0, -1):
        with pytest.raises(ValueError):
            sum_totient(10, mod)


def test_totient_sum_large_and_coprime_pairs():
    assert sum_totient(10**6) == 303963552392
    for limit in range(1, 40):
        pairs = sum(math.gcd(a, b) == 1 for a in range(1, limit + 1)
                    for b in range(1, limit + 1))
        assert 2 * sum_totient(limit) - 1 == pairs
