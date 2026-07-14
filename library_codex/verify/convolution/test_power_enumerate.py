import random

from library_codex.convolution.AdvancedSeries import (
    power_coefficient_enumerate,
    power_inner_product_enumerate,
)
from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD, fps_multiply


def test_power_enumeration_against_repeated_multiplication():
    rng = random.Random(701)
    for size in range(1, 35):
        for _ in range(20):
            polynomial = [rng.randrange(DEFAULT_MOD) for _ in range(size)]
            weights = [rng.randrange(DEFAULT_MOD) for _ in range(size)]
            multiplier = [rng.randrange(DEFAULT_MOD) for _ in range(size)]
            count = rng.randrange(35)
            inner = power_inner_product_enumerate(polynomial, weights, count)
            coefficient = power_coefficient_enumerate(
                polynomial, multiplier, count
            )
            power = [1]
            for exponent in range(count + 1):
                expected_inner = sum(
                    weights[index] * (power[index] if index < len(power) else 0)
                    for index in range(size)
                ) % DEFAULT_MOD
                product = fps_multiply(power, multiplier, DEFAULT_MOD)
                expected_coefficient = (
                    product[size - 1] if size - 1 < len(product) else 0
                )
                assert inner[exponent] == expected_inner
                assert coefficient[exponent] == expected_coefficient
                power = fps_multiply(power, polynomial, DEFAULT_MOD)[:size]

