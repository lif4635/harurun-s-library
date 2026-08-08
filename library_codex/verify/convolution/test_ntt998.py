import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.NTT import convolution_naive
from library_codex.convolution.NTT998 import (
    MOD,
    intt,
    multiply,
    ntt,
    square,
)


def test_ntt998_round_trip():
    rng = random.Random(998)
    for exponent in range(12):
        values = [rng.randrange(-MOD, 2 * MOD) for _ in range(1 << exponent)]
        expected = [value % MOD for value in values]
        assert ntt(values) is values
        assert intt(values) is values
        assert values == expected


def test_ntt998_multiply_and_square_against_naive():
    rng = random.Random(999)
    for _ in range(5000):
        first = [rng.randrange(-MOD, 2 * MOD) for _ in range(rng.randrange(100))]
        second = [rng.randrange(-MOD, 2 * MOD) for _ in range(rng.randrange(100))]
        assert multiply(first, second) == convolution_naive(first, second, MOD)
        assert square(first) == convolution_naive(first, first, MOD)


def test_ntt998_does_not_mutate_multiply_inputs():
    first = list(range(100))
    second = list(range(80))
    expected_first = first[:]
    expected_second = second[:]
    multiply(first, second)
    assert first == expected_first
    assert second == expected_second


def test_ntt998_length_limit():
    with pytest.raises(ValueError):
        ntt([0] * 3)


if __name__ == "__main__":
    test_ntt998_round_trip()
    test_ntt998_multiply_and_square_against_naive()
    test_ntt998_does_not_mutate_multiply_inputs()
    test_ntt998_length_limit()
