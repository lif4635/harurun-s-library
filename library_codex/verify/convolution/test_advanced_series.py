import random

from library_codex.convolution.AdvancedSeries import (
    composite_exponential,
    interpolate_geometric,
    limit_sum_polynomial_exponential,
    multipoint_evaluation_geometric,
    prefix_sum_polynomial,
    product_geometric_substitutions,
    sum_of_rationals,
    sum_polynomial_exponential,
)
from library_codex.convolution.FormalPowerSeries import (
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


def test_geometric_evaluation_interpolation_and_product():
    rng = random.Random(827)
    for size in range(1, 90):
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        initial = rng.randrange(1, MOD)
        ratio = rng.randrange(2, 100000)
        count = rng.randrange(size, size + 50)
        values = multipoint_evaluation_geometric(polynomial, initial, ratio, count)
        point = initial
        for value in values:
            assert value == fps_evaluate(polynomial, point)
            point = point * ratio % MOD
        samples = values[:size]
        assert interpolate_geometric(samples, initial, ratio) == polynomial

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
