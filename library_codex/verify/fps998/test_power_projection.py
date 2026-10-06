import random

import pytest

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.PowerProjection import power_coefficient, power_projection


def test_fps998_power_projection_against_naive():
    rng = random.Random(9985)
    for _ in range(1000):
        size = rng.randrange(1, 20)
        count = rng.randrange(25)
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        weights = [rng.randrange(MOD) for _ in range(size)]
        expected = []
        power = [1]
        for _ in range(count):
            expected.append(sum(
                weights[index] * power[index]
                for index in range(min(len(weights), len(power)))
            ) % MOD)
            power = multiply(power, polynomial)
        assert power_projection(polynomial, weights, count) == expected

        multiplier = [rng.randrange(MOD) for _ in range(rng.randrange(1, size + 1))]
        expected = []
        power = [1]
        degree = size - 1
        for _ in range(count):
            product = multiply(power, multiplier)
            expected.append(product[degree] if degree < len(product) else 0)
            power = multiply(power, polynomial)
        assert power_coefficient(polynomial, multiplier, count) == expected


def test_projection_unequal_lengths_and_padding():
    rng = random.Random(51005)
    for size in (1, 2, 3, 63, 64, 65, 127, 128, 129):
        for source_size in (1, size // 2 + 1, size + 7):
            polynomial = [0] + [rng.randrange(-MOD, MOD) for _ in range(source_size - 1)]
            weights = [rng.randrange(-MOD, MOD) for _ in range(size)]
            before = polynomial[:], weights[:]
            power = [1]
            expected = []
            for _ in range(size + 3):
                expected.append(sum(value * weight for value, weight in zip(power, weights)) % MOD)
                power = multiply(power, polynomial)[:size]
            assert power_projection(polynomial, weights, size + 3) == expected
            assert (polynomial, weights) == before


def test_projection_empty_inputs():
    assert power_projection([], [1], 3) == [0, 0, 0]
    assert power_projection([0, 1], [], 3) == [0, 0, 0]
    assert power_projection([0, 1], [3, 4], 0) == []
    with pytest.raises(ValueError):
        power_projection([0, 1], [3, 4], -1)
