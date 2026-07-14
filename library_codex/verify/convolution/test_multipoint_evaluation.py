import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.FormalPowerSeries import fps_evaluate
from library_codex.convolution.MultipointEvaluation import (
    ProductTree,
    interpolate_consecutive,
    multipoint_evaluation,
    polynomial_interpolation,
)


MOD = 998244353


def test_multipoint_random_against_horner():
    rng = random.Random(0)
    for _ in range(10000):
        polynomial = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(80))]
        points = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(60))]
        expected = [fps_evaluate(polynomial, point) for point in points]
        assert multipoint_evaluation(polynomial, points) == expected
        if points:
            tree = ProductTree(points)
            assert tree.evaluate(polynomial, 1) == expected
            assert tree.evaluate(polynomial, 17) == expected


def test_interpolation_random_recovers_polynomial():
    rng = random.Random(1)
    for _ in range(5000):
        size = rng.randrange(1, 60)
        points = rng.sample(range(1, 10**6), size)
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        values = [fps_evaluate(polynomial, point) for point in points]
        assert polynomial_interpolation(points, values) == polynomial
        tree = ProductTree(points)
        assert tree.interpolate(values) == polynomial
        assert tree.evaluate(tree.interpolate(values)) == values


def test_duplicate_empty_and_constant_cases():
    assert multipoint_evaluation([], []) == []
    assert multipoint_evaluation([], [1, 2, 3]) == [0, 0, 0]
    assert multipoint_evaluation([7], [1, 1, 2]) == [7, 7, 7]
    assert polynomial_interpolation([], []) == []
    assert polynomial_interpolation([5], [11]) == [11]
    with pytest.raises(ValueError):
        polynomial_interpolation([1, 1], [2, 2])
    with pytest.raises(ValueError):
        polynomial_interpolation([1, 2], [3])
    with pytest.raises(ValueError):
        ProductTree([1]).evaluate([1], 0)


def test_other_prime_and_points_equal_modulo():
    mod = 10**9 + 7
    rng = random.Random(2)
    size = 180
    points = rng.sample(range(1, 10**7), size)
    polynomial = [rng.randrange(mod) for _ in range(size)]
    values = multipoint_evaluation(polynomial, points, mod)
    assert polynomial_interpolation(points, values, mod) == polynomial
    with pytest.raises(ValueError):
        polynomial_interpolation([3, 3 + mod], [1, 1], mod)


def test_consecutive_interpolation():
    rng = random.Random(3)
    for _ in range(10000):
        size = rng.randrange(1, 100)
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        values = [fps_evaluate(polynomial, point) for point in range(size)]
        point = rng.randrange(-10**18, 10**18)
        assert interpolate_consecutive(values, point) == fps_evaluate(
            polynomial, point
        )
        known = rng.randrange(size)
        assert interpolate_consecutive(values, known + MOD) == values[known]


def test_large_without_recursion():
    size = 20000
    points = list(range(1, size + 1))
    polynomial = [index * index % MOD for index in range(size)]
    tree = ProductTree(points)
    values = tree.evaluate(polynomial)
    assert len(values) == size
    restored = tree.interpolate(values)
    assert restored == polynomial


if __name__ == "__main__":
    test_multipoint_random_against_horner()
    test_interpolation_random_recovers_polynomial()
    test_duplicate_empty_and_constant_cases()
    test_other_prime_and_points_equal_modulo()
    test_consecutive_interpolation()
    test_large_without_recursion()
