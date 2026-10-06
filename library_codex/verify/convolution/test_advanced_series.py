import random

from library_codex.fps.CompositeExponential import composite_exponential
from library_codex.polynomial.PrefixSumPolynomial import prefix_sum_polynomial
from library_codex.polynomial.ProductGeometricSubstitutions import product_geometric_substitutions
from library_codex.fps.SumOfRationals import sum_of_rationals
from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_evaluate,
    fps_inverse,
    fps_multiply,
)


MOD = DEFAULT_MOD


def test_sum_of_rationals_and_composite_exponential():
    rng = random.Random(1009)
    fractions = []
    expected = [0] * 80
    for _ in range(20):
        coefficient = rng.randrange(MOD)
        root = rng.randrange(MOD)
        fractions.append(([coefficient], [1, -root % MOD]))
        power = 1
        for index in range(len(expected)):
            expected[index] = (expected[index] + coefficient * power) % MOD
            power = power * root % MOD
    numerator, denominator = sum_of_rationals(fractions)
    actual = fps_multiply(numerator, fps_inverse(denominator, 80), MOD)[:80]
    assert actual == expected

    polynomial = [rng.randrange(MOD) for _ in range(30)]
    actual = composite_exponential(polynomial, 60)
    factorial = 1
    for exponent in range(60):
        if exponent:
            factorial = factorial * exponent % MOD
        expected_value = sum(
            coefficient * pow(index, exponent, MOD)
            for index, coefficient in enumerate(polynomial)
        ) % MOD * pow(factorial, -1, MOD) % MOD
        assert actual[exponent] == expected_value


def test_prefix_sum_polynomial():
    rng = random.Random(824)
    for size in range(1, 80):
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        result = prefix_sum_polynomial(polynomial)
        running = 0
        for point in range(size + 20):
            running = (running + fps_evaluate(polynomial, point)) % MOD
            assert fps_evaluate(result, point) == running


def test_product_geometric_substitutions():
    rng = random.Random(827)
    for _ in range(50):
        degree = rng.randrange(1, 70)
        polynomial = [1] + [rng.randrange(MOD) for _ in range(degree - 1)]
        ratio = rng.randrange(1, 1000)
        count = rng.randrange(20)
        actual = product_geometric_substitutions(polynomial, ratio, count)
        expected = [1]
        power = 1
        for _ in range(count):
            factor = [coefficient * pow(power, index, MOD) % MOD
                      for index, coefficient in enumerate(polynomial)]
            expected = fps_multiply(expected, factor, MOD)[:degree]
            power = power * ratio % MOD
        expected.extend([0] * (degree - len(expected)))
        assert actual == expected[:degree]
