import random

from library_codex.convolution.AdvancedSeries import (
    composite_exponential_scaled,
    inverse_composite_exponential,
)
from library_codex.convolution.StirlingMatrix import (
    stirling_matrix,
    stirling_matrix_transpose,
)


MOD = 998244353


def test_composite_exponential_inverse():
    rng = random.Random(811)
    for size in range(1, 100):
        values = [rng.randrange(MOD) for _ in range(size)]
        scale = rng.randrange(1, MOD)
        composed = composite_exponential_scaled(values, scale)
        assert inverse_composite_exponential(composed, scale) == values


def test_stirling_matrix_actions_against_quadratic_dp():
    rng = random.Random(812)
    for size in range(1, 80):
        second = [[0] * size for _ in range(size)]
        second[0][0] = 1
        for row in range(1, size):
            for column in range(1, row + 1):
                second[row][column] = (
                    second[row - 1][column - 1]
                    + column * second[row - 1][column]
                ) % MOD
        values = [rng.randrange(MOD) for _ in range(size)]
        expected = [sum(second[row][column] * values[column]
                        for column in range(size)) % MOD
                    for row in range(size)]
        expected_transpose = [sum(second[row][column] * values[row]
                                  for row in range(size)) % MOD
                              for column in range(size)]
        assert stirling_matrix(values) == expected
        assert stirling_matrix_transpose(values) == expected_transpose
        assert stirling_matrix(expected, inverse=True) == values
        assert stirling_matrix_transpose(
            expected_transpose, inverse=True
        ) == values

