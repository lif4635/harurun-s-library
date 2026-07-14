import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.convolution.AdvancedConvolution import (  # noqa: E402
    chirp_z,
    middle_product,
    multidimensional_dft,
    multiplicative_convolution_mod_prime,
    multivariate_circular_convolution,
    multivariate_multiplication,
)
from library_codex.convolution.NTT import convolution  # noqa: E402


MOD = 998244353


def test_chirp_z_and_middle_product_against_direct():
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
                second = [rng.randrange(MOD) for _ in range(rng.randrange(20))]
                product = convolution(polynomial, second)
                begin = rng.randrange(-5, 40)
                assert middle_product(polynomial, second, begin, count) == [
                    product[i] if 0 <= i < len(product) else 0
                    for i in range(begin, begin + count)
                ]


def _digits(index, base):
    result = []
    for radix in base:
        result.append(index % radix)
        index //= radix
    return result


def test_multivariate_truncated_and_circular_against_pairs():
    rng = random.Random(111)
    bases = [[], [2], [3], [2, 3], [3, 2, 2], [2, 2, 2, 2]]
    for base in bases:
        size = 1
        for radix in base:
            size *= radix
        for _ in range(300):
            first = [rng.randrange(MOD) for _ in range(size)]
            second = [rng.randrange(MOD) for _ in range(size)]
            truncated = [0] * size
            circular = [0] * size
            for i in range(size):
                di = _digits(i, base)
                for j in range(size):
                    dj = _digits(j, base)
                    coefficient = first[i] * second[j]
                    if all(a + b < radix
                           for a, b, radix in zip(di, dj, base)):
                        index = sum((a + b) * (1 if axis == 0 else
                            __import__('math').prod(base[:axis]))
                                    for axis, (a, b) in enumerate(zip(di, dj)))
                        truncated[index] += coefficient
                    wrapped = [(a + b) % radix
                               for a, b, radix in zip(di, dj, base)]
                    index = sum(value * (1 if axis == 0 else
                                __import__('math').prod(base[:axis]))
                                for axis, value in enumerate(wrapped))
                    circular[index] += coefficient
            truncated = [value % MOD for value in truncated]
            circular = [value % MOD for value in circular]
            assert multivariate_multiplication(first, second, base) == truncated
            if all((MOD - 1) % radix == 0 for radix in base):
                assert multivariate_circular_convolution(
                    first, second, base
                ) == circular


def test_multidimensional_dft_inverse():
    rng = random.Random(112)
    for base in ([2], [7], [2, 7], [2, 2, 7]):
        size = 1
        for radix in base:
            size *= radix
        for _ in range(100):
            values = [rng.randrange(MOD) for _ in range(size)]
            transformed = multidimensional_dft(values, base)
            assert multidimensional_dft(transformed, base, True) == values


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
            assert multiplicative_convolution_mod_prime(
                first, second, prime
            ) == expected
