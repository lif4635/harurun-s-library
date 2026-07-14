import math
import random

from library_codex.convolution.FormalPowerSeries import (
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_power,
)
from library_codex.convolution.SeriesSequences import (
    bell_numbers,
    bernoulli_numbers,
    circular_series,
    derangement_numbers,
    euler_transform,
    partition_numbers,
    pascal_transform,
    polynomial_mobius_transform,
    sparse_divide,
    sparse_exponential,
    sparse_inverse,
    sparse_logarithm,
    sparse_power,
    stirling_first_column,
    stirling_first_row,
    stirling_second_column,
    stirling_second_row,
)


MOD = 998244353


def test_famous_sequences_against_integer_recurrences():
    first = [[1]]
    second = [[1]]
    for n in range(1, 30):
        previous = first[-1]
        current = [0] * (n + 1)
        for k, value in enumerate(previous):
            current[k] += value * (n - 1)
            current[k + 1] += value
        first.append(current)
        previous = second[-1]
        current = [0] * (n + 1)
        for k in range(1, n + 1):
            current[k] = (previous[k - 1] if k else 0) + (
                previous[k] * k if k < len(previous) else 0
            )
        second.append(current)
        assert stirling_first_row(n) == [value % MOD for value in first[n]]
        assert stirling_second_row(n) == [value % MOD for value in second[n]]
    for column in range(8):
        assert stirling_first_column(column, 29) == [
            (first[n][column] if column <= n else 0) % MOD for n in range(30)
        ]
        assert stirling_second_column(column, 29) == [
            (second[n][column] if column <= n else 0) % MOD for n in range(30)
        ]

    partitions = [0] * 101
    partitions[0] = 1
    for part in range(1, 101):
        for total in range(part, 101):
            partitions[total] += partitions[total - part]
    assert partition_numbers(100) == [value % MOD for value in partitions]
    bells = [sum(second[n]) % MOD for n in range(30)]
    assert bell_numbers(29) == bells
    derangements = derangement_numbers(20)
    assert derangements[:5] == [1, 0, 1, 2, 9]
    exact_derangements = [1, 0]
    for n in range(2, 21):
        exact_derangements.append(
            (n - 1) * (exact_derangements[-1] + exact_derangements[-2])
        )
    assert derangements == [value % MOD for value in exact_derangements]
    bernoulli = bernoulli_numbers(20)
    assert bernoulli[:5] == [1, -pow(2, -1, MOD) % MOD, pow(6, -1, MOD), 0,
                             -pow(30, -1, MOD) % MOD]


def test_sparse_operations_against_dense_fps():
    rng = random.Random(31)
    for degree in (1, 2, 20, 100):
        series = [0] * degree
        series[0] = 1
        for _ in range(max(1, degree // 8)):
            series[rng.randrange(degree)] = rng.randrange(MOD)
        series[0] = 1
        numerator = [rng.randrange(MOD) for _ in range(degree)]
        assert sparse_inverse(series, degree) == fps_inverse(series, degree)
        assert sparse_divide(numerator, series, degree) == fps_multiply(
            numerator, fps_inverse(series, degree)
        )[:degree]
        logarithm = sparse_logarithm(series, degree)
        assert logarithm == fps_logarithm(series, degree)
        assert sparse_exponential(logarithm, degree) == fps_exponential(
            logarithm, degree
        )
        assert sparse_power(series, 7, degree) == fps_power(series, 7, degree)


def test_pascal_euler_circular_and_mobius():
    rng = random.Random(32)
    for size in range(1, 30):
        values = [rng.randrange(MOD) for _ in range(size)]
        direct = [sum(math.comb(i, j) * values[j] for j in range(i + 1)) % MOD
                  for i in range(size)]
        assert pascal_transform(values) == direct
        assert pascal_transform(direct, inverse=True) == values
        transposed = [sum(math.comb(j, i) * values[j] for j in range(i, size)) % MOD
                      for i in range(size)]
        assert pascal_transform(values, transpose=True) == transposed
        assert pascal_transform(transposed, inverse=True, transpose=True) == values

    exponents = [0, 2, 1, 3] + [0] * 20
    transformed = euler_transform(exponents)
    direct = [1] + [0] * 23
    for part in range(1, 4):
        for _ in range(exponents[part]):
            for total in range(part, 24):
                direct[total] = (direct[total] + direct[total - part]) % MOD
    assert transformed == direct

    angle = [0, 3, 5, 7, 11, 13]
    real, imaginary = circular_series(angle)
    product_real = fps_multiply(real, real)[:len(angle)]
    product_imag = fps_multiply(imaginary, imaginary)[:len(angle)]
    assert [(product_real[i] + product_imag[i]) % MOD
            for i in range(len(angle))] == [1] + [0] * (len(angle) - 1)

    polynomial = [2, 3, 5, 7, 11]
    transformed = polynomial_mobius_transform(polynomial, 13, 17, 19, 23)
    for x in (0, 1, 2, 3):
        ratio = (13 + 17 * x) * pow(19 + 23 * x, -1, MOD) % MOD
        left = sum(value * pow(x, i, MOD) for i, value in enumerate(transformed)) % MOD
        # Equality is only coefficient-wise up to degree; use x=0 for exact value.
        if x == 0:
            right = sum(value * pow(ratio, i, MOD)
                        for i, value in enumerate(polynomial)) % MOD
            assert left == right
