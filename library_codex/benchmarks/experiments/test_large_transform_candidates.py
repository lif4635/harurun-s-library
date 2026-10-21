import importlib
import random

import pytest

from library_codex.convolution import NTT998 as ntt


def naive(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return [x % ntt.MOD for x in result]


@pytest.mark.parametrize("name,lanes", [("large_unroll2", 16), ("large_unroll4", 16),
                                       ("large_thirtytwo_lanes", 32), ("large_nonnegative", 16),
                                       ("large_binary_first", 16), ("large_binary_first_fused", 16),
                                       ("large_streamed_product", 16), ("large_binary_unroll2", 16),
                                       ("large_binary_unroll2_positive", 16), ("large_radix8", 16),
                                       ("large_distributed_twiddles", 16), ("large_radix8_distributed", 16),
                                       ("large_radix8_medium", 16)])
def test_candidates(name, lanes):
    module = importlib.import_module("library_codex.benchmarks.experiments." + name)
    multiply = module._convolution_large_convolution_multiply_sixteen_lanes
    rng = random.Random(21991)
    for size in (1, 2, 4, 8, 16, 64, 256):
        for pattern in range(6):
            n = rng.randrange(1, lanes * size)
            m = lanes * size - n + 1
            if pattern == 0:
                a, b = [ntt.MOD - 1] * n, [ntt.MOD - 1] * m
            elif pattern == 1:
                a, b = [0] * n, [ntt.MOD - 1] * m
            else:
                a = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(n)]
                b = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(m)]
            saved = a[:], b[:]
            expected = naive(a, b) if n + m <= 256 else ntt.multiply(a, b)
            assert multiply(a, b, size) == expected, (name, size, pattern)
            assert (a, b) == saved
        a = [rng.randrange(ntt.MOD) for _ in range(lanes * size // 2)]
        assert multiply(a, a, size) == ntt.multiply(a, a)


@pytest.mark.parametrize("name", ["large_radix8", "large_radix8_distributed"])
def test_radix8_transforms(name):
    module = importlib.import_module("library_codex.benchmarks.experiments." + name)
    _radix8_forward, _radix8_inverse = module._radix8_forward, module._radix8_inverse

    rng = random.Random(21992)
    for height in range(13):
        for stride in (1, 4, 16):
            values = [rng.randrange(ntt.MOD) for _ in range(stride << height)]
            actual, expected = values[:], values[:]
            _radix8_forward(actual, stride)
            ntt._butterfly(expected, stride=stride)
            assert actual == expected, (height, stride)
            _radix8_inverse(actual, stride)
            assert actual == [x * (1 << height) % ntt.MOD for x in values]
