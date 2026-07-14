from itertools import permutations
import random

from library_codex.math.BlackBoxLinearAlgebra import (
    SparseMatrix,
    black_box_determinant,
    black_box_linear_solve,
    black_box_minimal_polynomial,
    black_box_power,
)
from library_codex.math.Matrix import (
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


def test_black_box_dense_and_sparse_operations():
    rng = random.Random(937841)
    for size in range(1, 18):
        for case in range(40):
            dense = [[0] * size for _ in range(size)]
            sparse = SparseMatrix(size)
            for row in range(size):
                for column in range(size):
                    if rng.randrange(4) == 0:
                        value = rng.randrange(MOD)
                        dense[row][column] = value
                        sparse.add(row, column, value)
            vector = [rng.randrange(MOD) for _ in range(size)]
            exponent = rng.randrange(1000)
            expected = matrix_vector_multiply(
                matrix_power(dense, exponent, MOD), vector, MOD
            )
            assert black_box_power(
                sparse, vector, exponent, MOD, case, 5
            ) == expected
            determinant = matrix_determinant(dense, MOD)
            assert black_box_determinant(
                sparse, MOD, case + 10000, 12
            ) == determinant


def test_black_box_minpoly_and_linear_solve():
    rng = random.Random(516829)
    for size in range(1, 40):
        diagonal = [rng.randrange(1, MOD) for _ in range(size)]
        while len(set(diagonal)) != size:
            diagonal = [rng.randrange(1, MOD) for _ in range(size)]
        matrix = [
            [diagonal[row] if row == column else 0 for column in range(size)]
            for row in range(size)
        ]
        vector = [rng.randrange(1, MOD) for _ in range(size)]
        polynomial = black_box_minimal_polynomial(
            matrix, MOD, vector, size, 4
        )
        assert len(polynomial) == size + 1
        solution = black_box_linear_solve(
            matrix, vector, MOD, size + 1, 4
        )
        assert matrix_vector_multiply(matrix, solution, MOD) == vector


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
