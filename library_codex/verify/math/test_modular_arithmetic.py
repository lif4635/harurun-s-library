import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.math.ModularArithmetic import (
    discrete_logarithm,
    modular_square_root,
)


def primes_below(limit):
    sieve = bytearray(b"\x01") * limit
    sieve[:2] = b"\x00\x00"
    for value in range(2, int(limit ** 0.5) + 1):
        if sieve[value]:
            sieve[value * value:limit:value] = b"\x00" * (
                (limit - 1 - value * value) // value + 1
            )
    return [value for value in range(limit) if sieve[value]]


def brute_log(base, target, modulus):
    target %= modulus
    value = 1 % modulus
    seen = set()
    exponent = 0
    while value not in seen:
        if value == target:
            return exponent
        seen.add(value)
        value = value * base % modulus
        exponent += 1
    return -1


def test_modular_square_root_all_small_primes():
    for prime in primes_below(3000):
        squares = {value * value % prime for value in range(prime)}
        for value in range(prime):
            root = modular_square_root(value, prime)
            if value in squares:
                assert 0 <= root < prime
                assert root * root % prime == value
                assert root <= (-root) % prime
            else:
                assert root == -1


def test_discrete_log_exhaustive_small():
    for modulus in range(1, 120):
        for base in range(modulus):
            for target in range(modulus):
                assert discrete_logarithm(base, target, modulus) == brute_log(
                    base, target, modulus
                )


def test_large_random_solvable_logs_and_square_roots():
    rng = random.Random(0)
    primes = (998244353, 10**9 + 7, 1000000000039)
    for _ in range(2000):
        prime = rng.choice(primes)
        value = rng.randrange(prime)
        square = value * value % prime
        root = modular_square_root(square, prime)
        assert root * root % prime == square
    for _ in range(300):
        modulus = rng.randrange(2, 10**7)
        base = rng.randrange(modulus)
        exponent = rng.randrange(10000)
        target = pow(base, exponent, modulus)
        found = discrete_logarithm(base, target, modulus)
        assert found != -1
        assert pow(base, found, modulus) == target
        assert found <= exponent
    with pytest.raises(ValueError):
        modular_square_root(1, 1)
    with pytest.raises(ValueError):
        discrete_logarithm(1, 1, 0)


if __name__ == "__main__":
    test_modular_square_root_all_small_primes()
    test_discrete_log_exhaustive_small()
    test_large_random_solvable_logs_and_square_roots()
