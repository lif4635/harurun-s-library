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


def test_planned_transforms_reuse_larger_tables():
    from library_codex.convolution.NTT998 import _butterfly, _butterfly_inv, _ntt_plan

    rng = random.Random(930)
    forward = _ntt_plan(4096)
    inverse = _ntt_plan(4096, True)
    saved = tuple(values.tobytes() for values in forward + inverse)
    for exponent in range(13):
        size = 1 << exponent
        source = [rng.randrange(-MOD, 2 * MOD) for _ in range(size)]
        actual = source[:]
        assert _butterfly(actual, forward) == ntt(source[:])
        assert _butterfly_inv(actual, inverse) == [value * size % MOD for value in source]
    assert tuple(values.tobytes() for values in forward + inverse) == saved


def test_partial_inverse_retains_every_requested_coefficient():
    from library_codex.convolution.NTT998 import _butterfly_inv, _ntt_plan

    rng = random.Random(931)
    tables = _ntt_plan(1024, True)
    for exponent in range(1, 11):
        size = 1 << exponent
        source = [rng.randrange(MOD) for _ in range(size)]
        transformed = ntt(source[:])
        for bit in (0, *(1 << k for k in range(exponent))):
            for plan in (None, tables):
                actual = _butterfly_inv(transformed[:], plan, bit)
                assert all(actual[i] == source[i] * size % MOD for i in range(size) if not i & bit)


def test_boundary_correction_cost_guard(monkeypatch):
    import importlib

    module = importlib.import_module("library_codex.convolution.NTT998")
    original = module._multiply_without_boundary
    lengths = []

    def record(first, second):
        lengths.append((len(first), len(second)))
        return original(first, second)

    monkeypatch.setattr(module, "_multiply_without_boundary", record)
    for first_size, second_size, trimmed in ((129, 129, 1), (128, 64, 0), (131687, 130552, 0)):
        result = module.multiply([1] * first_size, [1] * second_size)
        assert lengths[-1] == (first_size - trimmed, second_size)
        assert result == [min(i + 1, first_size, second_size, first_size + second_size - 1 - i)
                          for i in range(first_size + second_size - 1)]


if __name__ == "__main__":
    test_ntt998_round_trip()
    test_ntt998_multiply_and_square_against_naive()
    test_ntt998_does_not_mutate_multiply_inputs()
    test_ntt998_length_limit()
