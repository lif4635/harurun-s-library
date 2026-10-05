import random

import pytest

from library_codex.number_theory.MinMod import min_mod


def test_exhaustive_small():
    for modulus in range(1, 36):
        for a in range(modulus):
            for b in range(modulus):
                expected = modulus
                for n in range(1, 2 * modulus + 2):
                    expected = min(expected, (a * (n - 1) + b) % modulus)
                    assert min_mod(n, modulus, a, b) == expected


def test_signed_and_large_integers():
    rng = random.Random(1927)
    for _ in range(3000):
        n = rng.randrange(1, 100)
        modulus = rng.randrange(1, 10**30)
        a, b = rng.randrange(-10**60, 10**60), rng.randrange(-10**60, 10**60)
        assert min_mod(n, modulus, a, b) == min((a * i + b) % modulus for i in range(n))
    assert min_mod(10**100, 10**100 + 1, 10**100, 10**100) == 1
    assert min_mod(10**100 + 1, 10**100 + 1, 10**100, 10**100) == 0


def test_invalid():
    for args in [(0, 7, 1, 2), (-1, 7, 1, 2), (1, 0, 1, 2), (1, -3, 1, 2)]:
        with pytest.raises(ValueError):
            min_mod(*args)
