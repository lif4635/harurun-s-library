import importlib
import random

from library_codex.convolution import BinaryFieldConvolution as gf
from library_codex.convolution import NTT998 as ntt


def test_binary_arithmetic_candidates():
    rng = random.Random(21970)
    for name in ('binary_field_adaptive_fivebit', 'binary_field_radix8', 'binary_field_integer_fold',
                 'binary_field_linear_top', 'binary_field_linear10', 'binary_field_linear12', 'binary_field_linear14',
                 'binary_field_linear13', 'binary_field_linear14_bits4', 'binary_field_linear14_bits6',
                 'binary_field_nibble15', 'binary_field_nibble16', 'binary_field_nibble_shared',
                 'binary_field_linear_unbalanced'):
        module = importlib.import_module('library_codex.benchmarks.experiments.' + name)
        mask = (1 << 64) - 1
        values = [0, 1, mask, mask >> 1, mask >> 32]
        values += [rng.getrandbits(64) for _ in range(80)]
        values += [mask ^ (1 << i) for i in range(64)]
        for x in values:
            for y in values:
                assert module._compress(module._mul(module._expand(x), module._expand(y))) == gf._compress(gf._mul(gf._expand(x), gf._expand(y)))
        for n, m in ((9, 12), (17, 30), (129, 256), (510, 512), (1024, 1025), (1025, 8192)):
            a = [rng.getrandbits(64) for _ in range(n)]
            b = [rng.getrandbits(64) for _ in range(m)]
            assert module.multiply(a, b) == gf.multiply(a, b), (name, n, m)


def test_eight_lanes():
    module = importlib.import_module('library_codex.benchmarks.experiments.large_eight_lanes')
    rng = random.Random(21972)
    for n, m in ((1, 1), (3, 4), (7, 9), (127, 130), (4097, 7000), (8192, 8192)):
        for limit in (1, ntt.MOD):
            a = [rng.randrange(limit) if limit > 1 else ntt.MOD - 1 for _ in range(n)]
            b = [rng.randrange(limit) if limit > 1 else ntt.MOD - 1 for _ in range(m)]
            size = 1 << max(0, (n + m - 2).bit_length() - 3)
            assert module._convolution_large_convolution_multiply_four_lanes(a, b, size) == ntt.multiply(a, b)


def test_prescaled_lanes():
    rng = random.Random(21973)
    for name, lanes in (('large_prescaled_input', 4), ('large_eight_lanes_prescaled', 8),
                        ('large_eight_split', 8), ('large_eight_split_twice', 8), ('large_eight_karatsuba', 8),
                        ('large_sixteen_lanes', 16), ('large_sixteen_split', 16), ('large_sixteen_split_twice', 16)):
        module = importlib.import_module('library_codex.benchmarks.experiments.' + name)
        for n, m in ((1, 1), (3, 4), (127, 130), (4097, 7000)):
            a = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(n)]
            b = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(m)]
            size = 1 << max(0, (n + m - 2).bit_length() - (lanes.bit_length() - 1))
            assert module._convolution_large_convolution_multiply_four_lanes(a, b, size) == ntt.multiply(a, b)
            size = 1 << max(0, (2 * n - 2).bit_length() - (lanes.bit_length() - 1))
            assert module._convolution_large_convolution_multiply_four_lanes(a, a, size) == ntt.multiply(a, a)
        for period in (1, 2, 3, 4, 8):
            a = [ntt.MOD - 1 if (i // period) & 1 else 0 for i in range(1024)]
            b = a[::-1]
            assert module._convolution_large_convolution_multiply_four_lanes(a, b, 2048 // lanes) == ntt.multiply(a, b)


def test_large_arithmetic_candidates():
    rng = random.Random(21971)
    for name in ('large_lazy_forward', 'large_scaled_inverse', 'large_lazy_scaled'):
        module = importlib.import_module('library_codex.benchmarks.experiments.' + name)
        for height in range(1, 14):
            for stride in (1, 4):
                size = 1 << height
                a = [rng.randrange(ntt.MOD) for _ in range(size * stride)]
                expected = a[:]
                ntt._butterfly(expected, stride=stride)
                actual = a[:]
                module._convolution_ntt998_butterfly(actual, stride=stride)
                assert actual == expected, (name, height, stride, 'forward')
                options = dict(stride=stride)
                if name != 'large_lazy_forward':
                    options['scale'] = pow(size, ntt.MOD - 2, ntt.MOD)
                module._convolution_ntt998_butterfly_inv(actual, **options)
                assert actual == (a if 'scale' in options else [x * size % ntt.MOD for x in a])
        for n, m in ((1, 1), (3, 4), (127, 130), (4097, 7000)):
            a = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(n)]
            b = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(m)]
            size = 1 << max(0, (n + m - 2).bit_length() - 2)
            assert module._convolution_large_convolution_multiply_four_lanes(a, b, size) == ntt.multiply(a, b)
