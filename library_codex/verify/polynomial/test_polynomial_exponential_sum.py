import random

import pytest

from library_codex.fps.FormalPowerSeries import fps_evaluate
from library_codex.polynomial.PolynomialExponentialSum import (
    limit_sum_polynomial_exponential, sum_polynomial_exponential,
)


MOD = 998244353


def test_sum_of_polynomial_times_exponential():
    rng = random.Random(909)
    for degree in range(20):
        coefficients = [rng.randrange(MOD) for _ in range(degree + 1)]
        samples = [fps_evaluate(coefficients, point)
                   for point in range(degree + 1)]
        ratio = rng.randrange(2, 1000)
        for count in list(range(30)) + [10 ** 12 + 39]:
            actual = sum_polynomial_exponential(samples, ratio, count)
            if count < 30:
                expected = sum(pow(ratio, index, MOD)
                               * fps_evaluate(coefficients, index)
                               for index in range(count)) % MOD
                assert actual == expected
        limit = limit_sum_polynomial_exponential(samples, ratio)
        differences = samples[:]
        expected_limit = 0
        ratio_power = 1
        denominator_power = 1 - ratio
        for order in range(degree + 1):
            expected_limit += (differences[0] * ratio_power
                               * pow(denominator_power, -1, MOD))
            differences = [
                (differences[index + 1] - differences[index]) % MOD
                for index in range(len(differences) - 1)
            ]
            ratio_power = ratio_power * ratio % MOD
            denominator_power = denominator_power * (1 - ratio) % MOD
        assert limit == expected_limit % MOD


def test_zero_one_ratio_and_field_period():
    assert sum_polynomial_exponential([1], 1, 2) == 2
    for mod in (17, 101, MOD):
        for coefficients in ([1], [3, 2], [5, 4, 2]):
            values = [fps_evaluate(coefficients, i, mod) for i in range(len(coefficients))]
            saved = values[:]
            for ratio in (0, 1, mod, mod + 1, 2):
                for count in range(100):
                    expected = sum(pow(ratio, i, mod) * fps_evaluate(coefficients, i, mod) for i in range(count)) % mod
                    assert sum_polynomial_exponential(values, ratio, count, mod) == expected
                assert values == saved
            assert sum_polynomial_exponential(values, 1, mod * 10 ** 12 + 3, mod) == sum(fps_evaluate(coefficients, i, mod) for i in range(3)) % mod
            assert limit_sum_polynomial_exponential(values, 0, mod) == values[0]
    assert sum_polynomial_exponential([7], 2, 10 ** 18) == 7 * (pow(2, 10 ** 18, MOD) - 1) % MOD
    with pytest.raises(ValueError):
        sum_polynomial_exponential([], 2, 0)
    with pytest.raises(ValueError):
        limit_sum_polynomial_exponential([1], 1)


def test_large_count_difference_identity():
    for mod in (17, 101, MOD):
        coefficients = [3, 4, 7, 9]
        values = [fps_evaluate(coefficients, i, mod) for i in range(4)]
        for ratio in (0, 1, 2, mod - 1):
            for count in (mod - 1, mod, mod + 1, 10 ** 18 + 7):
                left = sum_polynomial_exponential(values, ratio, count, mod)
                right = sum_polynomial_exponential(values, ratio, count + 1, mod)
                assert (right - left) % mod == pow(ratio, count, mod) * fps_evaluate(coefficients, count, mod) % mod
