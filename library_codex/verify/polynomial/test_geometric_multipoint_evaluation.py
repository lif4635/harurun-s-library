import random

import pytest

from library_codex.fps.FormalPowerSeries import fps_evaluate
from library_codex.polynomial.GeometricMultipointEvaluation import (
    interpolate_geometric, multipoint_evaluation_geometric,
)


MOD = 998244353


def test_geometric_evaluation_interpolation():
    rng = random.Random(827)
    for size in range(1, 90):
        polynomial = [rng.randrange(MOD) for _ in range(size)]
        initial = rng.randrange(1, MOD)
        ratio = rng.randrange(2, 100000)
        count = rng.randrange(size, size + 50)
        values = multipoint_evaluation_geometric(polynomial, initial, ratio, count)
        point = initial
        for value in values:
            assert value == fps_evaluate(polynomial, point)
            point = point * ratio % MOD
        samples = values[:size]
        assert interpolate_geometric(samples, initial, ratio) == polynomial


def test_degenerate_and_repeated_points():
    assert interpolate_geometric([], 0, 0) == []
    assert interpolate_geometric([-1], 0, 0, 17) == [16]
    assert interpolate_geometric([5, 3], 2, 0) == [3, 1]
    for initial, ratio, values in [(0, 3, [1, 2]), (1, 1, [1, 2]), (1, 0, [1, 2, 3]), (1, -1, [1, 2, 3])]:
        with pytest.raises(ValueError):
            interpolate_geometric(values, initial, ratio)
    assert multipoint_evaluation_geometric([], 0, 0, 3) == [0, 0, 0]
    assert multipoint_evaluation_geometric([1, 2], 0, 3, 3) == [1, 1, 1]
    assert multipoint_evaluation_geometric([1, 2], 3, 1, 3) == [7, 7, 7]
    assert multipoint_evaluation_geometric([1, 2], 3, 0, 3) == [7, 1, 1]
    assert multipoint_evaluation_geometric([1], 3, 2, 0) == []
    with pytest.raises(ValueError):
        multipoint_evaluation_geometric([1], 3, 2, -1)


def test_other_primes_and_root_of_unity():
    rng = random.Random(4827)
    for mod, ratio, sizes in [(17, 3, range(1, 17)), (101, 2, range(1, 31)), (MOD, 3, [127, 128, 129, 255, 256, 257])]:
        for size in sizes:
            polynomial = [rng.randrange(mod) for _ in range(size)]
            values = multipoint_evaluation_geometric(polynomial, 5, ratio, size, mod)
            saved = values[:]
            assert values == [fps_evaluate(polynomial, 5 * pow(ratio, i, mod), mod) for i in range(size)]
            assert interpolate_geometric(values, 5, ratio, mod) == polynomial
            assert values == saved
    size = 128
    ratio = pow(3, (MOD - 1) // size, MOD)
    polynomial = list(range(size))
    values = multipoint_evaluation_geometric(polynomial, 1, ratio, size)
    assert interpolate_geometric(values, 1, ratio) == polynomial
