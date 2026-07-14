import itertools
import random
import sys
from math import gcd
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.math.ChineseRemainder import (
    chinese_remainder,
    chinese_remainder_balanced,
    garner_mod,
    inv_gcd,
)


def brute(residues, moduli):
    modulus = 1
    for value in moduli:
        modulus = modulus * value // gcd(modulus, value)
    for candidate in range(modulus):
        if all(
            candidate % mod == value % mod
            for value, mod in zip(residues, moduli)
        ):
            return candidate, modulus
    return 0, 0


def test_exhaustive_small_against_brute():
    assert chinese_remainder([], []) == (0, 1)
    for size in range(1, 4):
        for moduli in itertools.product(range(1, 9), repeat=size):
            ranges = [range(-1, modulus + 1) for modulus in moduli]
            for residues in itertools.product(*ranges):
                expected = brute(residues, moduli)
                assert chinese_remainder(residues, moduli) == expected
                assert chinese_remainder_balanced(residues, moduli) == expected


def test_inv_gcd_and_random_systems():
    rng = random.Random(0)
    for _ in range(100000):
        modulus = rng.randrange(1, 10**12)
        value = rng.randrange(-10**18, 10**18)
        common, inverse = inv_gcd(value, modulus)
        assert common == gcd(value, modulus)
        assert value * inverse % modulus == common % modulus
    for _ in range(10000):
        size = rng.randrange(20)
        moduli = [rng.randrange(1, 10**6) for _ in range(size)]
        solution = rng.randrange(-10**30, 10**30)
        residues = [solution % modulus for modulus in moduli]
        sequential = chinese_remainder(residues, moduli)
        balanced = chinese_remainder_balanced(residues, moduli)
        assert sequential == balanced
        assert all(sequential[0] % m == r for r, m in zip(residues, moduli))


def test_garner_mod_pairwise_coprime():
    rng = random.Random(1)
    primes = [101, 103, 107, 109, 113, 127, 131, 137]
    for _ in range(10000):
        size = rng.randrange(len(primes) + 1)
        moduli = rng.sample(primes, size)
        residues = [rng.randrange(modulus) for modulus in moduli]
        target = rng.randrange(1, 10**9)
        exact, _ = chinese_remainder(residues, moduli)
        assert garner_mod(residues, moduli, target) == exact % target
    with pytest.raises(ValueError):
        garner_mod([1, 1], [6, 10], 1000)
    with pytest.raises(ValueError):
        chinese_remainder([1], [])


if __name__ == "__main__":
    test_exhaustive_small_against_brute()
    test_inv_gcd_and_random_systems()
    test_garner_mod_pairwise_coprime()
