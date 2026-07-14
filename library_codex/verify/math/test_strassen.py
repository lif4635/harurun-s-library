import random

from library_codex.math.Strassen import strassen_matrix_multiply


def _naive(first, second, mod=None):
    result = [[0] * len(second[0]) for _ in first]
    for row in range(len(first)):
        for pivot in range(len(second)):
            for column in range(len(second[0])):
                result[row][column] += first[row][pivot] * second[pivot][column]
        if mod is not None:
            result[row] = [value % mod for value in result[row]]
    return result


def test_strassen_rectangular_against_naive():
    rng = random.Random(737)
    for rows, inner, columns in (
        (1, 1, 1), (3, 5, 2), (17, 13, 19), (33, 35, 31), (65, 61, 67)
    ):
        first = [[rng.randrange(-100, 101) for _ in range(inner)]
                 for _ in range(rows)]
        second = [[rng.randrange(-100, 101) for _ in range(columns)]
                  for _ in range(inner)]
        assert strassen_matrix_multiply(
            first, second, mod=None, threshold=8
        ) == _naive(first, second)
        assert strassen_matrix_multiply(
            first, second, mod=998244353, threshold=8
        ) == _naive(first, second, 998244353)

