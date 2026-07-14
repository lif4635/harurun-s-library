import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.FormalPowerSeries import (
    fps_multiply,
    fps_square_root,
)
from library_codex.convolution.PolynomialComposition import (
    fps_compose,
    fps_compositional_inverse,
)


MOD = 998244353


def naive_compose(outer, inner, degree, mod=MOD):
    result = []
    for coefficient in reversed(outer[:degree]):
        result = fps_multiply(result, inner, mod)[:degree]
        if result:
            result[0] = (result[0] + coefficient) % mod
        else:
            result = [coefficient % mod]
    result.extend([0] * (degree - len(result)))
    return result


def test_composition_random_against_naive():
    rng = random.Random(0)
    for _ in range(3000):
        degree = rng.randrange(1, 180)
        outer = [rng.randrange(MOD) for _ in range(rng.randrange(220))]
        inner = [rng.randrange(MOD) for _ in range(rng.randrange(220))]
        assert fps_compose(outer, inner, degree) == naive_compose(
            outer, inner, degree
        )


def test_composition_other_prime_fallback_and_edges():
    mod = 10**9 + 7
    rng = random.Random(1)
    for _ in range(100):
        degree = rng.randrange(65, 180)
        outer = [rng.randrange(mod) for _ in range(degree)]
        inner = [rng.randrange(mod) for _ in range(degree)]
        assert fps_compose(outer, inner, degree, mod) == naive_compose(
            outer, inner, degree, mod
        )
    assert fps_compose([], [1, 2], 5) == [0] * 5
    assert fps_compose([1, 2, 3], [], 5) == [1, 0, 0, 0, 0]
    assert fps_compose([1, 2, 3], [0, 1], 5) == [1, 2, 3, 0, 0]
    assert fps_compose([1, 2, 3], [7], 5) == [162, 0, 0, 0, 0]


def test_fps_square_root_random_squares_and_failures():
    rng = random.Random(2)
    for mod in (MOD, 10**9 + 7):
        for _ in range(2000):
            degree = rng.randrange(1, 160)
            root = [rng.randrange(mod) for _ in range(rng.randrange(160))]
            square = fps_multiply(root, root, mod)[:degree]
            square.extend([0] * (degree - len(square)))
            found = fps_square_root(square, degree, mod)
            assert found is not None
            assert fps_multiply(found, found, mod)[:degree] == square
    assert fps_square_root([0, 1], 2) is None
    assert fps_square_root([3], 1, 7) is None
    assert fps_square_root([], 10) == [0] * 10


def test_compositional_inverse_random():
    rng = random.Random(3)
    identity = [0, 1]
    for _ in range(500):
        degree = rng.randrange(2, 180)
        series = [0, rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(degree - 2)
        ]
        inverse = fps_compositional_inverse(series, degree)
        expected = identity + [0] * (degree - 2)
        assert fps_compose(series, inverse, degree) == expected
        assert fps_compose(inverse, series, degree) == expected
    with pytest.raises(ValueError):
        fps_compositional_inverse([1, 1], 2)
    with pytest.raises(ZeroDivisionError):
        fps_compositional_inverse([0, 0], 2)


def test_large_without_recursion():
    degree = 100000
    outer = [1] * degree
    composed = fps_compose(outer, [0, 1, 1], degree)
    expected = [0] * degree
    expected[0] = expected[1] = 1
    for index in range(2, degree):
        expected[index] = (expected[index - 1] + expected[index - 2]) % MOD
    assert composed == expected
    series = [0, 3] + [0] * (degree - 2)
    inverse = fps_compositional_inverse(series, degree)
    assert inverse[0] == 0
    assert inverse[1] == pow(3, -1, MOD)
    assert not any(inverse[2:])


if __name__ == "__main__":
    test_composition_random_against_naive()
    test_composition_other_prime_fallback_and_edges()
    test_fps_square_root_random_squares_and_failures()
    test_compositional_inverse_random()
    test_large_without_recursion()
