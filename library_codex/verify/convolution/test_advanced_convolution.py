import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.convolution.ChirpZ import chirp_z  # noqa: E402
from library_codex.convolution.MiddleProduct import middle_product  # noqa: E402
from library_codex.arithmetic_convolution.MultiplicativeConvolutionModPrime import (  # noqa: E402
    multiplicative_convolution,
)
from library_codex.convolution.NTT import convolution  # noqa: E402


MOD = 998244353


def test_chirp_z_against_direct():
    rng = random.Random(110)
    for length in range(30):
        for count in range(30):
            for _ in range(20):
                polynomial = [rng.randrange(MOD) for _ in range(length)]
                ratio = rng.randrange(MOD)
                start = rng.randrange(MOD)
                expected = []
                point = start
                for _ in range(count):
                    value = 0
                    for coefficient in reversed(polynomial):
                        value = (value * point + coefficient) % MOD
                    expected.append(value)
                    point = point * ratio % MOD
                assert chirp_z(polynomial, ratio, count, start) == expected


def test_middle_product_against_direct_correlation():
    rng = random.Random(114)
    sizes = ((1, 1), (8, 3), (61, 61), (127, 63), (128, 67), (257, 129))
    for first_size, second_size in sizes:
        for _ in range(12):
            first = [rng.randrange(MOD) for _ in range(first_size)]
            second = [rng.randrange(MOD) for _ in range(second_size)]
            expected = [
                sum(second[j] * first[i + j] for j in range(second_size)) % MOD
                for i in range(first_size - second_size + 1)
            ]
            first_before = first[:]
            second_before = second[:]
            assert middle_product(first, second) == expected
            assert first == first_before
            assert second == second_before


def test_middle_product_rejects_invalid_lengths():
    for first, second in (([], []), ([1], []), ([1], [1, 2])):
        try:
            middle_product(first, second)
        except ValueError:
            pass
        else:
            raise AssertionError((first, second))


def test_multiplicative_convolution_mod_prime():
    rng = random.Random(113)
    for prime in (2, 3, 5, 7, 11, 13, 17):
        for _ in range(300):
            first = [rng.randrange(MOD) for _ in range(prime)]
            second = [rng.randrange(MOD) for _ in range(prime)]
            expected = [0] * prime
            for i in range(prime):
                for j in range(prime):
                    expected[i * j % prime] += first[i] * second[j]
            expected = [value % MOD for value in expected]
            assert multiplicative_convolution(
                first, second, prime
            ) == expected
