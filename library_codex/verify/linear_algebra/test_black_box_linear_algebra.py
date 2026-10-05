import random

from library_codex.linear_algebra.BlackBoxLinearAlgebra import (
    SparseMatrix,
    black_box_determinant,
    black_box_linear_solve,
    black_box_minimal_polynomial,
    black_box_power,
)
from library_codex.linear_algebra.Matrix import (
    matrix_determinant,
    matrix_power,
    matrix_vector_multiply,
)


MOD = 998244353


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
