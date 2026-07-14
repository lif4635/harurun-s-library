import random

from library_codex.convolution.AdvancedConvolution import multivariate_multiplication
from library_codex.convolution.MultivariateFPS import MultivariateFPS


def test_multivariate_fps_arithmetic_and_transcendentals():
    rng = random.Random(422)
    for base in ((2, 3), (3, 3), (2, 2, 2)):
        size = 1
        for radix in base:
            size *= radix
        for _ in range(20):
            first = [rng.randrange(998244353) for _ in range(size)]
            second = [rng.randrange(998244353) for _ in range(size)]
            left = MultivariateFPS(first, base)
            right = MultivariateFPS(second, base)
            assert (left * right).f == multivariate_multiplication(
                first, second, base
            )
            first[0] = 1
            unit = MultivariateFPS(first, base)
            inverse = unit.inv()
            assert (unit * inverse).f == [1] + [0] * (size - 1)
            logarithm = unit.log()
            assert logarithm.exp().f == unit.f


def test_multivariate_indexing():
    series = MultivariateFPS(base=(2, 3, 4))
    series.set(1, 2, 3, 91)
    assert series.get(1, 2, 3) == 91
    assert series.index(1, 2, 3) == 1 + 2 * 2 + 3 * 6

