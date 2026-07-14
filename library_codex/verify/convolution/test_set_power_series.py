import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.SetFunction import (
    SubsetConvolution,
    set_series_composition,
    set_series_exponential,
    set_series_power_projection,
)


MOD = 998244353


def brute_composition(outer, series):
    engine = SubsetConvolution()
    size = len(series)
    result = [0] * size
    power = [1] + [0] * (size - 1)
    for coefficient in outer:
        for mask, value in enumerate(power):
            result[mask] = (result[mask] + coefficient * value) % MOD
        power = engine.multiply(power, series)
    return result


def brute_projection(series, weights, terms):
    engine = SubsetConvolution()
    size = len(series)
    result = []
    power = [1] + [0] * (size - 1)
    for _ in range(terms):
        result.append(sum(
            power[mask] * weights[mask] for mask in range(size)
        ) % MOD)
        power = engine.multiply(power, series)
    return result


def test_composition_random_against_powers():
    rng = random.Random(0)
    for bits in range(8):
        size = 1 << bits
        for _ in range(500):
            series = [rng.randrange(MOD) for _ in range(size)]
            outer = [rng.randrange(MOD) for _ in range(rng.randrange(12))]
            assert set_series_composition(outer, series) == brute_composition(
                outer, series
            )


def test_power_projection_random_and_adjoint():
    rng = random.Random(1)
    for bits in range(8):
        size = 1 << bits
        for _ in range(500):
            series = [rng.randrange(MOD) for _ in range(size)]
            weights = [rng.randrange(MOD) for _ in range(size)]
            terms = rng.randrange(15)
            expected = brute_projection(series, weights, terms)
            result = set_series_power_projection(series, weights, terms)
            assert result == expected
            exponential = set_series_power_projection(
                series, weights, terms, exponential=True
            )
            factorial = 1
            for index in range(terms):
                if index:
                    factorial = factorial * index % MOD
                assert exponential[index] * factorial % MOD == expected[index]

            outer = [rng.randrange(MOD) for _ in range(terms)]
            composed = set_series_composition(outer, series)
            left = sum(
                composed[mask] * weights[mask] for mask in range(size)
            ) % MOD
            right = sum(
                outer[index] * result[index] for index in range(terms)
            ) % MOD
            assert left == right


def test_exponential_as_polynomial_composition():
    rng = random.Random(2)
    for bits in range(10):
        size = 1 << bits
        series = [0] + [rng.randrange(MOD) for _ in range(size - 1)]
        inverse_factorial = [1] * (bits + 1)
        factorial = 1
        for index in range(1, bits + 1):
            factorial = factorial * index % MOD
            inverse_factorial[index] = pow(factorial, -1, MOD)
        assert set_series_composition(
            inverse_factorial, series
        ) == set_series_exponential(series)


def test_large_without_recursion():
    bits = 16
    size = 1 << bits
    series = [index % 1000 for index in range(size)]
    weights = [(index * index + 1) % MOD for index in range(size)]
    outer = [index * 17 % MOD for index in range(40)]
    composed = set_series_composition(outer, series)
    projected = set_series_power_projection(series, weights, 40)
    assert len(composed) == size
    assert len(projected) == 40
    assert sum(c * w for c, w in zip(composed, weights)) % MOD == sum(
        a * b for a, b in zip(outer, projected)
    ) % MOD


if __name__ == "__main__":
    test_composition_random_against_powers()
    test_power_projection_random_and_adjoint()
    test_exponential_as_polynomial_composition()
    test_large_without_recursion()
