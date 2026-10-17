import random

import pytest

from library_codex.arithmetic_convolution.MultiplicativeConvolutionModPowerOfTwo import multiplicative_convolution_pow2


def _naive(a, b):
    result = [0] * len(a)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i * j & (len(a) - 1)] += x * y
    return [value % 998244353 for value in result]


def test_random_against_quadratic_convolution():
    rng = random.Random(108348)
    for exponent in range(9):
        for _ in range(6):
            a = [rng.randrange(-998244353, 998244353) for _ in range(1 << exponent)]
            b = [rng.randrange(-998244353, 998244353) for _ in a]
            saved_a, saved_b = a.copy(), b.copy()
            assert multiplicative_convolution_pow2(a, b) == _naive(a, b)
            assert (a, b) == (saved_a, saved_b)
            assert multiplicative_convolution_pow2(a, a) == _naive(a, a)


def test_sparse_inputs_and_absorbing_zero():
    for exponent in range(7):
        size = 1 << exponent
        for i in range(size):
            for j in range(size):
                a = [0] * size
                b = [0] * size
                a[i] = 2
                b[j] = 3
                expected = [0] * size
                expected[i * j & (size - 1)] = 6
                assert multiplicative_convolution_pow2(a, b) == expected


def test_invalid_lengths():
    for a, b in (([], []), ([1], []), ([1], [1, 2]), ([1] * 3, [2] * 3)):
        with pytest.raises(ValueError):
            multiplicative_convolution_pow2(a, b)
