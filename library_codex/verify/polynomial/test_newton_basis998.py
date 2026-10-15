import random
import pytest

from library_codex.polynomial.NewtonBasis998 import MOD, from_newton, to_newton


def naive(coefficients, points):
    result = [0] * len(coefficients)
    basis = [1]
    for coefficient, point in zip(coefficients, points):
        for j, value in enumerate(basis):
            result[j] = (result[j] + coefficient * value) % MOD
        following = [0] * (len(basis) + 1)
        for j, value in enumerate(basis):
            following[j] = (following[j] - point * value) % MOD
            following[j + 1] = value
        basis = following
    return result


def test_random_against_expansion():
    rng = random.Random(7321)
    for n in list(range(40)) + [63, 64, 65, 127, 128, 129, 257]:
        for _ in range(8):
            coefficients = [rng.randrange(-MOD, MOD) for _ in range(n)]
            points = [rng.randrange(-5, 6) for _ in range(n)]
            expected = naive(coefficients, points)
            assert from_newton(coefficients, points) == expected
            assert to_newton(expected, points) == [value % MOD for value in coefficients]


def test_zeros_repeated_points_and_preservation():
    for n in [0, 1, 2, 33, 1000]:
        values = list(range(n))
        points = [0] * n
        assert to_newton(values, points) == values
        assert from_newton(values, points) == values
        assert to_newton([0] * n, [4] * n) == [0] * n
        assert from_newton([0] * n, [4] * n) == [0] * n
        assert values == list(range(n))
        assert points == [0] * n
    assert to_newton([2, 3, 1], [1, 2, 99]) == [6, 6, 1]


def test_lengths():
    for function in (to_newton, from_newton):
        with pytest.raises(ValueError):
            function([1], [])
