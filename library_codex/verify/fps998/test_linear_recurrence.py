import random

import pytest

from library_codex.fps998.LinearRecurrence import (
    MOD, berlekamp_massey, bostan_mori, linear_recurrence_nth,
    linear_recurrence_slice, nth_term,
)
from library_codex.convolution.NTT998 import multiply


def test_linear_recurrence_family():
    rng = random.Random(9984)
    for _ in range(1000):
        order = rng.randrange(1, 15)
        coefficients = [rng.randrange(MOD) for _ in range(order)]
        initial = [rng.randrange(MOD) for _ in range(order)]
        sequence = initial[:]
        while len(sequence) < 80:
            sequence.append(sum(coefficients[i] * sequence[-1 - i]
                                for i in range(order)) % MOD)
        index = rng.randrange(80)
        assert linear_recurrence_nth(initial, coefficients, index) == sequence[index]
        assert len(berlekamp_massey(sequence[:40])) <= order
        assert nth_term(index, sequence[:40]) == sequence[index]
        denominator = [1] + [-value % MOD for value in coefficients]
        numerator = multiply(initial, denominator)[:order]
        assert bostan_mori(index, numerator, denominator) == sequence[index]


def test_bostan_mori_ntt_path_against_series_expansion():
    rng = random.Random(20260809)
    for _ in range(100):
        denominator = [rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(rng.randrange(60, 150))
        ]
        numerator = [rng.randrange(MOD) for _ in range(rng.randrange(50, 180))]
        index = rng.randrange(400)
        inverse = pow(denominator[0], MOD - 2, MOD)
        result = []
        for i in range(index + 1):
            value = numerator[i] if i < len(numerator) else 0
            for offset in range(1, min(i + 1, len(denominator))):
                value -= denominator[offset] * result[i - offset]
            result.append(value * inverse % MOD)
        assert bostan_mori(index, numerator, denominator) == result[index]


def test_slice_against_naive():
    rng = random.Random(70129)
    for order in (0, 1, 2, 3, 7, 16, 31, 65, 100):
        for trial in range(15):
            initial = [rng.randrange(-MOD, MOD) for _ in range(order)]
            coefficients = [rng.randrange(-MOD, MOD) for _ in range(order)]
            if trial % 3 == 0:
                coefficients[order // 2:] = [0] * (order - order // 2)
            values = [value % MOD for value in initial]
            for i in range(order, 330):
                values.append(sum(coefficients[j] * values[i - 1 - j]
                                  for j in range(order)) % MOD)
            for start, count in ((0, 0), (0, 200), (1, 130), (93, 203), (300, 20)):
                assert linear_recurrence_slice(initial, coefficients, start, count) == values[start:start + count]


def test_slice_huge_index():
    rng = random.Random(8215)
    for order in (1, 2, 7, 65, 129):
        initial = [rng.randrange(MOD) for _ in range(order)]
        coefficients = [rng.randrange(MOD) for _ in range(order)]
        for start in (10**6, 10**18):
            result = linear_recurrence_slice(initial, coefficients, start, 5)
            assert result == [linear_recurrence_nth(initial, coefficients, start + i) for i in range(5)]


def test_slice_boundaries_and_input_preservation():
    initial = [5, 7, 11]
    coefficients = [0, 0, 0]
    assert linear_recurrence_slice(initial, coefficients, 1, 5) == [7, 11, 0, 0, 0]
    assert linear_recurrence_slice(initial, coefficients, 10**18, 3) == [0, 0, 0]
    assert linear_recurrence_slice([3], [2], 10**18, 3) == [3 * pow(2, 10**18 + i, MOD) % MOD for i in range(3)]
    assert initial == [5, 7, 11]
    assert coefficients == [0, 0, 0]
    for start, count in ((-1, 3), (0, -1)):
        with pytest.raises(ValueError):
            linear_recurrence_slice([1], [1], start, count)
    with pytest.raises(ValueError):
        linear_recurrence_slice([1, 2], [1], 0, 0)
    assert bostan_mori(10, [1], [1, -1, -1]) == 89
