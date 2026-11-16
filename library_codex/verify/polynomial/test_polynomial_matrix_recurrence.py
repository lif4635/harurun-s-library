import random
import pytest
from library_codex.polynomial.PolynomialMatrixRecurrence import linear_matrix_recurrence


def test_matrix_products_against_stepwise_recurrence():
    rng = random.Random(61443)
    mod = 998244353
    for dimension in (1, 2, 3):
        for steps in (0, 1, 63, 65, 100, 233):
            initial = [rng.randrange(mod) for _ in range(dimension)]
            a = [[rng.randrange(mod) for _ in range(dimension)] for _ in range(dimension)]
            b = [[rng.randrange(mod) for _ in range(dimension)] for _ in range(dimension)]
            state = initial[:]
            for t in range(steps):
                inv = pow(t + 1, -1, mod)
                state = [sum((a[i][j] + t * b[i][j]) * state[j] for j in range(dimension)) % mod * inv % mod for i in range(dimension)]
            assert linear_matrix_recurrence(initial, a, b, (1, 1), steps) == state


def test_singular_denominator_and_noncommuting_matrices():
    with pytest.raises(ValueError):
        linear_matrix_recurrence([1], [[1]], [[0]], (0, 1), 100)
    with pytest.raises(ValueError):
        linear_matrix_recurrence([1, 2], [[1]], [[0]], (1, 0), 1)
    assert linear_matrix_recurrence([3], [[0]], [[0]], (1, 0), 100) == [0]
