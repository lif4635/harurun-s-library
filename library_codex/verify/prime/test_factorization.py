import random
import sys
from math import prod
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.prime.Factorization import (
    divisors,
    euler_phi,
    factor_count,
    is_prime,
    mobius,
    pollard_rho,
    prime_factors,
)


def test_primality_exhaustive_and_pseudoprimes():
    limit = 500000
    sieve = bytearray(b"\x01") * limit
    sieve[:2] = b"\x00\x00"
    for value in range(2, int(limit ** 0.5) + 1):
        if sieve[value]:
            sieve[value * value:limit:value] = b"\x00" * (
                (limit - 1 - value * value) // value + 1
            )
    for value in range(limit):
        assert is_prime(value) == bool(sieve[value])
    composites = (
        341550071728321,
        3825123056546413051,
        18446744073709551615,
    )
    for value in composites:
        assert not is_prime(value)
    assert is_prime(18446744073709551557)
    with pytest.raises(ValueError):
        is_prime(1 << 64)


def test_factorization_random_constructed_numbers():
    rng = random.Random(0)
    primes = [value for value in range(2, 10000) if is_prime(value)]
    for _ in range(10000):
        factors = []
        number = 1
        for _ in range(rng.randrange(1, 12)):
            prime = rng.choice(primes)
            if number * prime >= 1 << 64:
                break
            number *= prime
            factors.append(prime)
        assert prime_factors(number) == sorted(factors)
        counts = factor_count(number)
        assert prod(prime ** exponent for prime, exponent in counts.items()) == number
        assert all(is_prime(prime) for prime in counts)


def test_hard_64bit_numbers_and_pollard_factor():
    numbers = (
        1000000007 * 1000000009,
        4294967291 * 4294967279,
        18446744073709551615,
        4294967291 * 4294967291,
    )
    for number in numbers:
        factors = prime_factors(number)
        assert prod(factors) == number
        assert all(is_prime(factor) for factor in factors)
        factor = pollard_rho(number)
        assert 1 < factor < number
        assert number % factor == 0


def test_divisors_phi_mobius_and_validation():
    for number in range(1, 5000):
        expected = [value for value in range(1, number + 1) if number % value == 0]
        assert divisors(number) == expected
        assert euler_phi(number) == sum(
            1 for value in range(1, number + 1)
            if __import__("math").gcd(value, number) == 1
        )
        counts = factor_count(number)
        expected_mobius = 0 if any(value > 1 for value in counts.values()) else (
            -1 if len(counts) & 1 else 1
        )
        assert mobius(number) == expected_mobius
    with pytest.raises(ValueError):
        prime_factors(0)
    with pytest.raises(ValueError):
        divisors(0)


if __name__ == "__main__":
    test_primality_exhaustive_and_pseudoprimes()
    test_factorization_random_constructed_numbers()
    test_hard_64bit_numbers_and_pollard_factor()
    test_divisors_phi_mobius_and_validation()
