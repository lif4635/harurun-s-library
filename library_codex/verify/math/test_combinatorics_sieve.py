import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.math.Combinatorics import (  # noqa: E402
    Combination,
    enumerate_quotient,
    extended_gcd,
    floor_sum,
    gray_code,
    inverse_gray_code,
    mod_affine_range_count,
)
from library_codex.prime.Sieve import (  # noqa: E402
    LinearSieve,
    count_square_free,
    prime_count,
    prime_sieve,
)


def test_extended_gcd_combination_and_gray():
    rng = random.Random(100)
    for _ in range(10_000):
        a = rng.randrange(-10**18, 10**18)
        b = rng.randrange(-10**18, 10**18)
        gcd, x, y = extended_gcd(a, b)
        assert gcd == math.gcd(a, b)
        assert a * x + b * y == gcd
    combination = Combination(mod=998244353)
    for n in range(500):
        for k in range(n + 1):
            assert combination.binomial(n, k) == math.comb(n, k) % 998244353
    for value in range(10_000):
        assert inverse_gray_code(gray_code(value)) == value


def test_floor_sum_and_mod_affine_against_direct_sum():
    rng = random.Random(101)
    for _ in range(5_000):
        n = rng.randrange(100)
        modulus = rng.randrange(1, 100)
        multiplier = rng.randrange(-200, 201)
        addend = rng.randrange(-200, 201)
        assert floor_sum(n, modulus, multiplier, addend) == sum(
            (multiplier * i + addend) // modulus for i in range(n)
        )
        y = rng.randrange(modulus + 1)
        assert mod_affine_range_count(
            multiplier, addend, modulus, n, y
        ) == sum((multiplier * i + addend) % modulus < y for i in range(n))


def test_enumerate_quotient_ranges():
    for number in range(1_000):
        ranges = list(enumerate_quotient(number))
        flattened = []
        for quotient, left, right in ranges:
            assert left < right
            assert all(number // value == quotient for value in range(left, right))
            flattened.extend(range(left, right))
        assert flattened == list(range(1, number + 1))


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
        expected = sum(prime <= number for prime in primes)
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
