import importlib
import random
import pytest

from library_codex.convolution import BinaryFieldConvolution as gf
from library_codex.convolution import NTT998 as ntt


def test_binary_candidates():
    rng = random.Random(20261021)
    modules = [importlib.import_module('library_codex.benchmarks.experiments.' + name)
               for name in ('binary_field_xor_reduce', 'binary_field_zero_top',
                            'binary_field_tile256', 'binary_field_tile4096',
                            'binary_field_fold_table', 'binary_field_fold_tile256')]
    for n, m in ((1, 7), (9, 10), (128, 128), (129, 199), (511, 512),
                 (1024, 1024), (1025, 1025), (4096, 4096), (4095, 2049)):
        a = [rng.getrandbits(64) for _ in range(n)]
        b = [rng.getrandbits(64) for _ in range(m)]
        expected = gf.multiply(a, b)
        for module in modules:
            assert module.multiply(a, b) == expected, (module.__name__, n, m)
    for a in (0, 1, (1 << 64) - 1, (1 << 64) - 2):
        for b in (0, 1, (1 << 64) - 1, (1 << 64) - 2):
            x, y = gf._expand(a), gf._expand(b)
            for module in modules:
                assert module._mul(x, y) == gf._mul(x, y)


def test_large_cache_transforms():
    module = importlib.import_module('library_codex.benchmarks.experiments.large_cache_tiled')
    rng = random.Random(72813)
    for height in range(17):
        values = [rng.randrange(ntt.MOD) for _ in range(1 << height)]
        expected = values[:]
        ntt._butterfly(expected)
        actual = values[:]
        module._convolution_ntt998_butterfly(actual)
        assert actual == expected, ('forward', height)
        ntt._butterfly_inv(expected)
        module._convolution_ntt998_butterfly_inv(actual)
        assert actual == expected, ('inverse', height)


def test_binary_fivebit_split():
    module = importlib.import_module('library_codex.benchmarks.experiments.binary_field_fivebit_split')
    rng = random.Random(54387)
    mask = (1 << 64) - 1
    values = [0, 1, mask, (1 << 32) - 1, mask ^ ((1 << 32) - 1)]
    values += [mask ^ (1 << i) for i in range(64)]
    for a in values:
        for b in values:
            actual = module._compress(module._mul(module._expand(a), module._expand(b)))
            expected = gf._compress(gf._mul(gf._expand(a), gf._expand(b)))
            assert actual == expected
    for n, m in ((9, 17), (1024, 1025), (2049, 257)):
        a = [rng.getrandbits(64) for _ in range(n)]
        b = [rng.getrandbits(64) for _ in range(m)]
        assert module.multiply(a, b) == gf.multiply(a, b)


@pytest.mark.parametrize('name', ('large_joint_lanes', 'large_joint_preallocated',
                                 'large_joint_zero_top', 'large_joint_karatsuba', 'large_joint_fused'))
def test_large_joint_lanes(name):
    module = importlib.import_module('library_codex.benchmarks.experiments.' + name)
    rng = random.Random(12981)
    for height in range(15):
        size = 1 << height
        values = [rng.randrange(ntt.MOD) for _ in range(4 * size)]
        expected = values[:]
        for lane in range(4):
            work = values[lane::4]
            ntt._butterfly(work)
            expected[lane::4] = work
        actual = values[:]
        module._lanes_forward(actual)
        assert actual == expected, ('joint forward', height)
        module._lanes_inverse(actual)
        assert actual == [x * size % ntt.MOD for x in values], ('joint inverse', height)
    for n, m in ((1, 1), (3, 4), (63, 45), (4097, 7000)):
        a = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(n)]
        b = [rng.randrange(-ntt.MOD, ntt.MOD) for _ in range(m)]
        size = 1 << max(0, (n + m - 2).bit_length() - 2)
        expected = ntt.multiply(a, b)
        assert module._convolution_large_convolution_multiply_four_lanes(a, b, size) == expected
        size = 1 << max(0, (2 * n - 2).bit_length() - 2)
        assert module._convolution_large_convolution_multiply_four_lanes(a, a, size) == ntt.multiply(a, a)
