from itertools import permutations
import random

from library_codex.convolution.FormalPowerSeries import (
    fps_add,
    fps_multiply,
)
from library_codex.convolution.MultipointEvaluation import sample_point_shift
from library_codex.math.Matrix import (
    identity_matrix,
    matrix_multiply,
)
from library_codex.math.PolynomialMatrix import (
    determinant_a_plus_xb,
    polynomial_matrix_determinant,
    polynomial_matrix_prefix_product,
    spanning_tree_polynomial,
)


MOD = 998244353


def evaluate(polynomial, point):
    result = 0
    for coefficient in reversed(polynomial):
        result = (result * point + coefficient) % MOD
    return result


def brute_polynomial_determinant(matrix):
    size = len(matrix)
    result = []
    for order in permutations(range(size)):
        product = [1]
        inversions = 0
        for row, column in enumerate(order):
            product = fps_multiply(product, matrix[row][column], MOD)
            for earlier in range(row):
                inversions += order[earlier] > column
        if inversions & 1:
            product = [-value % MOD for value in product]
        result = fps_add(result, product, MOD)
    return result or [0]


def test_sample_point_shift_random_polynomials():
    rng = random.Random(813749)
    for degree in range(60):
        for _ in range(100):
            polynomial = [rng.randrange(MOD) for _ in range(degree + 1)]
            samples = [evaluate(polynomial, point) for point in range(degree + 1)]
            point = rng.randrange(-2 * MOD, 2 * MOD)
            count = rng.randrange(80)
            shifted = sample_point_shift(samples, point, count, MOD)
            assert shifted == [
                evaluate(polynomial, point + index) for index in range(count)
            ]


def test_polynomial_matrix_determinant_against_permutations():
    rng = random.Random(519837)
    for size in range(5):
        for _ in range(500):
            matrix = [
                [
                    [rng.randrange(MOD) for _ in range(rng.randrange(1, 5))]
                    for _ in range(size)
                ]
                for _ in range(size)
            ]
            expected = brute_polynomial_determinant(matrix)
            actual = polynomial_matrix_determinant(matrix, MOD)
            expected.extend([0] * (len(actual) - len(expected)))
            assert actual == expected[:len(actual)]


def test_determinant_a_plus_xb_and_singular_fallback():
    rng = random.Random(719384)
    for size in range(8):
        for case in range(300):
            first = [[rng.randrange(MOD) for _ in range(size)] for _ in range(size)]
            second = [[rng.randrange(MOD) for _ in range(size)] for _ in range(size)]
            expected = polynomial_matrix_determinant(
                [[[first[i][j], second[i][j]] for j in range(size)] for i in range(size)],
                MOD,
            )
            assert determinant_a_plus_xb(
                first, second, MOD, case, 5
            ) == expected
    zero = [[0] * 5 for _ in range(5)]
    assert determinant_a_plus_xb(zero, zero, MOD, 1, 2) == [0] * 6


def test_polynomial_matrix_prefix_product_against_naive():
    rng = random.Random(981374)
    for size in range(1, 5):
        for case in range(250):
            matrix = [
                [
                    [rng.randrange(MOD) for _ in range(rng.randrange(1, 5))]
                    for _ in range(size)
                ]
                for _ in range(size)
            ]
            count = rng.randrange(100)
            expected = identity_matrix(size)
            for point in range(count):
                current = [
                    [evaluate(matrix[row][column], point) for column in range(size)]
                    for row in range(size)
                ]
                expected = matrix_multiply(current, expected, MOD)
            assert polynomial_matrix_prefix_product(
                matrix, count, MOD
            ) == expected


def test_polynomial_matrix_large_prefix_and_tree():
    matrix = [[[3, 2]]]
    count = 100000
    expected = 1
    for point in range(count):
        expected = expected * (3 + 2 * point) % MOD
    assert polynomial_matrix_prefix_product(matrix, count, MOD) == [[expected]]
    for size in range(2, 15):
        edges = [
            (first, second, [1, first + second + 1])
            for first in range(size)
            for second in range(first)
        ]
        polynomial = spanning_tree_polynomial(size, edges, MOD)
        for point in range(len(polynomial) + 2):
            numeric = [
                (first, second, evaluate(weight, point))
                for first, second, weight in edges
            ]
            from library_codex.math.AdvancedMatrix import spanning_tree_count

            assert evaluate(polynomial, point) == spanning_tree_count(
                size, numeric, MOD
            )
