from itertools import permutations
import random

import pytest

from library_codex.linear_algebra.Matrix import (
    characteristic_polynomial,
    inverse_matrix,
    linear_equation,
    matrix_determinant,
    matrix_multiply,
    matrix_power,
    matrix_rank,
    matrix_vector_multiply,
    sparse_linear_equation,
)


MOD = 998244353


def _product(first, second, mod):
    width = len(second[0]) if second else 0
    return [[sum(first[i][k] * second[k][j] for k in range(len(second))) % mod
             for j in range(width)] for i in range(len(first))]


def test_matrix_product_modular_accumulation_boundaries():
    rng = random.Random(20261005)
    for mod in (1, 2, 101, MOD, 1 << 30, (1 << 30) + 1, (1 << 89) - 1, -101):
        for inner in (0, 1, 7, 8, 9, 15, 16, 17, 33):
            for sparse in (False, True):
                first = [[rng.randrange(-mod * mod, mod * mod + 1)
                          if not sparse or rng.randrange(5) == 0 else 0
                          for _ in range(inner)] for _ in range(3)]
                second = [[rng.randrange(-mod * mod, mod * mod + 1)
                           for _ in range(5)] for _ in range(inner)]
                saved = ([row[:] for row in first], [row[:] for row in second])
                assert matrix_multiply(first, second, mod) == _product(first, second, mod)
                assert (first, second) == saved
            first = [[mod - 1] * inner] * 3
            second = [[mod - 1] * 5 for _ in range(inner)]
            assert matrix_multiply(first, second, mod) == _product(first, second, mod)
    assert matrix_multiply([], []) == []
    assert matrix_multiply([[], []], []) == [[], []]
    for first, second in (([[1, 2], [3]], [[1], [2]]), ([[1]], [[1], [2]]),
                          ([[1, 2]], [[1], [2, 3]])):
        with pytest.raises(ValueError):
            matrix_multiply(first, second)


def test_matrix_power_against_repeated_product():
    rng = random.Random(620510)
    for mod in (2, 101, MOD, (1 << 61) - 1):
        for size in range(7):
            matrix = [[rng.randrange(-mod, 2 * mod) for _ in range(size)]
                      for _ in range(size)]
            expected = [[int(i == j) for j in range(size)] for i in range(size)]
            saved = [row[:] for row in matrix]
            for exponent in range(15):
                assert matrix_power(matrix, exponent, mod) == expected
                expected = _product(expected, matrix, mod)
            assert matrix == saved
    with pytest.raises(ValueError):
        matrix_power([[1, 2]], 2)
    with pytest.raises(ValueError):
        matrix_power([[1]], -1)


def brute_determinant(matrix, mod=MOD):
    size = len(matrix)
    result = 0
    for order in permutations(range(size)):
        inversions = 0
        product = 1
        for row, column in enumerate(order):
            product = product * matrix[row][column] % mod
            for other in range(row):
                inversions += order[other] > column
        result += -product if inversions & 1 else product
    return result % mod


def evaluate(polynomial, value, mod=MOD):
    result = 0
    for coefficient in reversed(polynomial):
        result = (result * value + coefficient) % mod
    return result


def test_dense_matrix_determinant_inverse_and_rank():
    rng = random.Random(819374)
    for size in range(7):
        for _ in range(300):
            matrix = [
                [rng.randrange(MOD) for _ in range(size)]
                for _ in range(size)
            ]
            determinant = matrix_determinant(matrix, MOD)
            assert determinant == brute_determinant(matrix, MOD)
            inverse = inverse_matrix(matrix, MOD)
            if determinant == 0:
                assert inverse is None
            else:
                assert matrix_multiply(matrix, inverse, MOD) == [
                    [int(row == column) for column in range(size)]
                    for row in range(size)
                ]
                assert matrix_rank(matrix, MOD) == size


def test_characteristic_polynomial_by_evaluation():
    rng = random.Random(513897)
    for size in range(9):
        for _ in range(300):
            matrix = [
                [rng.randrange(MOD) for _ in range(size)]
                for _ in range(size)
            ]
            polynomial = characteristic_polynomial(matrix, MOD)
            assert len(polynomial) == size + 1
            assert polynomial[-1] == 1
            for value in range(size + 2):
                shifted = [row[:] for row in matrix]
                for index in range(size):
                    shifted[index][index] = value - shifted[index][index]
                for row in range(size):
                    for column in range(size):
                        if row != column:
                            shifted[row][column] = -shifted[row][column]
                assert evaluate(polynomial, value) == matrix_determinant(
                    shifted, MOD
                )


def test_linear_equation_particular_and_kernel():
    rng = random.Random(274891)
    for height in range(1, 8):
        for width in range(8):
            for _ in range(200):
                matrix = [
                    [rng.randrange(11) for _ in range(width)]
                    for _ in range(height)
                ]
                expected = [rng.randrange(11) for _ in range(width)]
                vector = matrix_vector_multiply(matrix, expected, 11)
                solution = linear_equation(matrix, vector, 11)
                assert solution is not None
                particular, basis = solution
                assert matrix_vector_multiply(matrix, particular, 11) == vector
                assert len(basis) == width - matrix_rank(matrix, 11)
                for direction in basis:
                    assert matrix_vector_multiply(matrix, direction, 11) == [
                        0
                    ] * height
    assert linear_equation([[0], [0]], [0, 1], 11) is None


def test_sparse_linear_equation_general_and_banded():
    rng = random.Random(618937)
    for height in range(1, 25):
        for width in range(25):
            for _ in range(50):
                dense = [[0] * width for _ in range(height)]
                sparse = []
                for row in range(height):
                    values = {}
                    for column in range(width):
                        if rng.randrange(8) == 0:
                            value = rng.randrange(101)
                            dense[row][column] = value
                            values[column] = value
                    sparse.append(values)
                expected = [rng.randrange(101) for _ in range(width)]
                vector = matrix_vector_multiply(dense, expected, 101)
                result = sparse_linear_equation(
                    sparse, vector, width, 101
                )
                assert result is not None
                assert matrix_vector_multiply(dense, result, 101) == vector
    size = 500
    sparse = []
    expected = [rng.randrange(101) for _ in range(size)]
    for row in range(size):
        sparse.append({
            column: rng.randrange(1, 101)
            for column in range(row, min(size, row + 5))
        })
        sparse[row][row] = 1
    vector = [
        sum(value * expected[column] for column, value in row.items()) % 101
        for row in sparse
    ]
    result = sparse_linear_equation(sparse, vector, size, 101, 5)
    assert result == expected
    assert sparse_linear_equation([{}], [1], 1, 101) is None
