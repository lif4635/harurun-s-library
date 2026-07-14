from math import gcd
import random

import pytest

from library_codex.math.ModularRoot import (
    ceil_kth_root,
    floor_kth_root,
    modular_kth_root,
    primitive_root,
)
from library_codex.prime.Factorization import factor_count, is_prime


def test_primitive_root_small_and_large_primes():
    primes = [number for number in range(2, 1000) if is_prime(number)]
    primes += [998244353, 1000000007, 2305843009213693951]
    for prime in primes:
        root = primitive_root(prime)
        assert pow(root, prime - 1, prime) == 1
        for divisor in factor_count(prime - 1):
            assert pow(root, (prime - 1) // divisor, prime) != 1


def test_modular_kth_root_exhaustive_small_primes():
    primes = [number for number in range(2, 200) if is_prime(number)]
    for prime in primes:
        for exponent in range(12):
            for value in range(prime):
                root = modular_kth_root(value, exponent, prime)
                brute = [
                    candidate
                    for candidate in range(prime)
                    if pow(candidate, exponent, prime) == value
                ]
                if brute:
                    assert root != -1
                    assert pow(root, exponent, prime) == value
                else:
                    assert root == -1


def test_modular_kth_root_random_generated_and_impossible():
    rng = random.Random(9483721)
    primes = [998244353, 1000000007, 1000000009, 2305843009213693951]
    for prime in primes:
        for _ in range(300):
            exponent = rng.randrange(1, 10**12)
            original = rng.randrange(prime)
            value = pow(original, exponent, prime)
            root = modular_kth_root(value, exponent, prime)
            assert root != -1
            assert pow(root, exponent, prime) == value
        for _ in range(300):
            exponent = rng.randrange(1, 10**12)
            value = rng.randrange(1, prime)
            common = gcd(exponent, prime - 1)
            root = modular_kth_root(value, exponent, prime)
            exists = pow(value, (prime - 1) // common, prime) == 1
            assert (root != -1) == exists
            if root != -1:
                assert pow(root, exponent, prime) == value


def test_integral_kth_roots_random_and_boundaries():
    rng = random.Random(183749)
    values = [0, 1, 2, (1 << 64) - 1, 10**1000]
    values += [rng.randrange(1 << 256) for _ in range(4000)]
    exponents = [1, 2, 3, 4, 5, 7, 16, 63, 64, 255, 1000]
    for value in values:
        for exponent in exponents:
            root = floor_kth_root(value, exponent)
            assert pow(root, exponent) <= value
            assert pow(root + 1, exponent) > value
            ceiling = ceil_kth_root(value, exponent)
            assert ceiling == root or ceiling == root + 1
            assert pow(ceiling, exponent) >= value


def test_root_argument_errors():
    with pytest.raises(ValueError):
        modular_kth_root(1, -1, 7)
    with pytest.raises(ValueError):
        modular_kth_root(1, 2, 1)
    with pytest.raises(ValueError):
        floor_kth_root(-1, 2)
    with pytest.raises(ValueError):
        floor_kth_root(1, 0)
