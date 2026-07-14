import math
import random

from library_codex.math.AlgebraExtras import (
    FloatBinomial,
    RationalBinomial,
    QBinomial,
    digamma,
    inverse_sum,
    pisano_period,
    power_table,
    semiring_linear_recurrence,
    semiring_matrix_power,
)


def test_semiring_matrix_and_recurrence():
    infinity = 10 ** 9
    add = min
    multiply = lambda first, second: first + second
    matrix = [[0, 3, infinity], [infinity, 0, 5], [2, infinity, 0]]
    power = semiring_matrix_power(matrix, 5, add, multiply, infinity, 0)
    brute = [[0 if i == j else infinity for j in range(3)] for i in range(3)]
    for _ in range(5):
        brute = [[min(brute[i][k] + matrix[k][j] for k in range(3))
                  for j in range(3)] for i in range(3)]
    assert power == brute
    mod = 998244353
    initial = [0, 1]
    coefficients = [1, 1]
    for index in range(100):
        a, b = 0, 1
        for _ in range(index):
            a, b = b, (a + b) % mod
        assert semiring_linear_recurrence(
            initial, coefficients, index,
            lambda x, y: (x + y) % mod,
            lambda x, y: x * y % mod, 0, 1
        ) == a


def test_float_and_rational_binomial_and_inverse_sum():
    table = FloatBinomial(1000)
    rational = RationalBinomial()
    for n in range(100):
        for k in range(n + 1):
            assert abs(math.exp(table.logC(n, k)) - math.comb(n, k)) < max(
                1e-6, math.comb(n, k) * 1e-11
            )
            assert rational.C(n, k) == math.comb(n, k)
    for left in (0.5, 1.0, 3.25, 100.0):
        for count in (1, 2, 10, 100):
            right = left + count
            expected = sum(1 / (left + index) for index in range(count))
            assert abs(inverse_sum(left, right) - expected) < 1e-11


def test_pisano_period_and_power_table():
    for modulus in range(1, 300):
        first, second = 0, 1 % modulus
        period = 0
        while True:
            first, second = second, (first + second) % modulus
            period += 1
            if first == 0 and second == 1 % modulus:
                break
        assert pisano_period(modulus) == period
    assert power_table(100, 37, 1000000007) == [
        pow(value, 37, 1000000007) for value in range(101)
    ]


def test_q_binomial_against_pascal_recurrence():
    mod = 998244353
    for q in (1, -1, 2, 3, 7):
        table = QBinomial(q, 100, mod)
        rows = [[1]]
        for n in range(1, 50):
            row = [0] * (n + 1)
            row[0] = row[n] = 1
            for k in range(1, n):
                row[k] = (rows[-1][k] + pow(q, n - k, mod) * rows[-1][k - 1]) % mod
            rows.append(row)
            for k in range(n + 1):
                assert table.binomial(n, k) == row[k]
