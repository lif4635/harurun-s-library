from array import array
import random
import subprocess
import sys

import pytest

from library_codex.convolution.BinaryFieldConvolution import (
    _basis, _compress, _convert, _expand, _mul, _transform, multiply,
)


def product(a, b):
    result = 0
    for bit in range(64):
        if b >> bit & 1:
            result ^= a << bit
    for bit in range(result.bit_length() - 1, 63, -1):
        if result >> bit & 1:
            result ^= ((1 << 64) | 27) << (bit - 64)
    return result


def naive(a, b):
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] ^= product(x, y)
    return result


def test_field_product_and_representation():
    rng = random.Random(92471)
    values = [0, 1, (1 << 64) - 1] + [1 << i for i in range(64)]
    for a in values:
        assert _compress(_expand(a)) == a
        for b in values:
            assert _compress(_mul(_expand(a), _expand(b))) == product(a, b)
    for _ in range(2000):
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        assert _compress(_mul(_expand(a), _expand(b))) == product(a, b)
    assert multiply([1 << 63], [2]) == [27]
    assert multiply([3], [3]) == [5]


def test_cantor_basis():
    basis = [_compress(x) for x in _basis()]
    assert len(basis) == 64 and basis[0] == 1
    pivots = {}
    for i, x in enumerate(basis):
        if i:
            assert product(x, x) ^ x == basis[i - 1]
        while x:
            bit = x.bit_length()
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
        assert x


def test_fft_is_polynomial_evaluation():
    rng = random.Random(2751)
    basis = _basis()
    for height in range(7):
        n = 1 << height
        values = [rng.getrandbits(64) for _ in range(n)]
        wide = [_expand(x) for x in values]
        constants = [0] * max(1, n // 2)
        for i in range(1, len(constants)):
            bit = i & -i
            constants[i] = constants[i ^ bit] ^ basis[bit.bit_length()]
        _convert(wide)
        _transform(wide, constants)
        for i in range(n):
            x = 0
            for j in range(height):
                if i >> j & 1:
                    x ^= _compress(basis[j])
            answer = 0
            for coefficient in reversed(values):
                answer = product(answer, x) ^ coefficient
            assert _compress(wide[i]) == answer
        _transform(wide, constants, True)
        _convert(wide, True)
        assert [_compress(x) for x in wide] == values


def test_boundaries_random_and_nonmutation():
    rng = random.Random(21719)
    lengths = [0, 1, 2, 8, 9, 15, 16, 17, 31, 33, 65]
    for n in lengths:
        for m in lengths:
            a = [rng.getrandbits(64) for _ in range(n)]
            b = [rng.getrandbits(64) for _ in range(m)]
            before = a[:], b[:]
            assert multiply(a, b) == naive(a, b)
            assert (a, b) == before
        assert multiply(a, a) == naive(a, a)
        assert multiply([0] * n, a) == naive([0] * n, a)
    assert multiply((1, 2), array("Q", [3, 4])) == [3, 2, 8]
    for bad in (-1, 1 << 64):
        with pytest.raises(ValueError):
            multiply([bad], [1])
        with pytest.raises(ValueError):
            multiply([1] * 9, [bad] * 9)


def test_bilinearity_and_lengths():
    rng = random.Random(14221)
    a, b, c = ([rng.getrandbits(64) for _ in range(129)] for _ in range(3))
    ab, ac = multiply(a, b), multiply(a, c)
    assert multiply(a, [x ^ y for x, y in zip(b, c)]) == [x ^ y for x, y in zip(ab, ac)]
    assert len(multiply([1] + [0] * 64, [1] + [0] * 128)) == 193


def test_high_level_basis_conversion_roundtrip():
    rng = random.Random(2146)
    for height in (8, 9, 16, 17):
        values = [0] * (1 << height)
        for _ in range(100):
            values[rng.randrange(len(values))] = _expand(rng.getrandbits(64))
        before = values[:]
        _convert(values)
        _convert(values, True)
        assert values == before


def test_conversion_and_fused_stages_match_scalar():
    from library_codex.convolution.BinaryFieldConvolution import _constants
    from library_codex.benchmarks.baselines.binary_field_scalar import (
        _constants as scalar_constants, _convert as scalar_convert, _transform as scalar_transform,
        _expand as scalar_expand, _compress as scalar_compress,
    )

    rng = random.Random(8135)
    for height in range(13):
        source = [rng.getrandbits(64) for _ in range(1 << height)]
        a = [scalar_expand(x) for x in source]
        b = [_expand(x) for x in source]
        scalar_convert(a)
        _convert(b)
        assert [scalar_compress(x) for x in a] == [_compress(x) for x in b]
        constants = _constants(len(a))
        old_constants = scalar_constants(len(a))
        scalar_transform(a, old_constants)
        _transform(b, constants)
        assert [scalar_compress(x) for x in a] == [_compress(x) for x in b]
        _transform(b, constants, True)
        _convert(b, True)
        scalar_transform(a, old_constants, True)
        scalar_convert(a, True)
        assert [scalar_compress(x) for x in a] == [_compress(x) for x in b] == source


def test_equal_distinct_inputs_use_square(monkeypatch):
    import importlib
    module = importlib.import_module("library_codex.convolution.BinaryFieldConvolution")

    def unexpected(*args):
        raise AssertionError("equal inputs should not require FFT")

    monkeypatch.setattr(module, "_transform", unexpected)
    rng = random.Random(7103)
    for size in (9, 17, 1024):
        a = [rng.getrandbits(64) for _ in range(size)]
        expected = [0] * (2 * size - 1)
        expected[::2] = [product(x, x) for x in a]
        assert multiply(a, tuple(a)) == expected
        assert multiply(a, a[:]) == expected


def test_signed_basis_conversion_preserves_unsigned_bits():
    from library_codex.convolution.BinaryFieldConvolution import _signed
    from library_codex.benchmarks.baselines.binary_field_scalar import _convert as reference

    rng = random.Random(18945)
    for height in (2, 3, 8, 12):
        values = [0, (1 << 63) - 1, 1 << 63, (1 << 64) - 1]
        values.extend(rng.getrandbits(64) for _ in range((1 << height) - 4))
        signed = _signed(values)
        expected = values[:]
        assert all(-(1 << 63) <= x < 1 << 63 for x in signed)
        _convert(signed)
        reference(expected)
        assert [x & ((1 << 64) - 1) for x in signed] == expected
        _convert(signed, True)
        assert [x & ((1 << 64) - 1) for x in signed] == values


def test_sixbit_multiplication_carry_boundary():
    from library_codex.benchmarks.baselines import binary_field_signed as reference

    mask = (1 << 64) - 1
    values = [0, 1, mask] + [mask ^ (1 << i) for i in range(64)]
    rng = random.Random(1695)
    pairs = [(a, b) for a in values for b in values]
    pairs.extend((rng.getrandbits(64), rng.getrandbits(64)) for _ in range(1000))
    for a, b in pairs:
        assert _compress(_mul(_expand(a), _expand(b))) == product(a, b)
    for n, m in ((9, 9), (17, 31), (65, 63), (257, 129)):
        a = [rng.choice(values) for _ in range(n)]
        b = [rng.choice(values) for _ in range(m)]
        assert multiply(a, b) == reference.multiply(a, b)


def test_final_reduction_table():
    from library_codex.convolution.BinaryFieldConvolution import _FOLD

    assert len(_FOLD) == 4162
    for bits in range(8):
        high = (bits & 1) | ((bits & 2) << 5) | ((bits & 4) << 10)
        assert _FOLD[high] == high ^ high << 6 ^ high << 18 ^ high << 24
    for a in range(1 << 61, 1 << 64, 1 << 61):
        for b in range(1 << 61, 1 << 64, 1 << 61):
            assert _compress(_mul(_expand(a), _expand(b))) == product(a, b)


def test_standalone(tmp_path):
    from library_codex.tools.build_library_catalog import ROOT, build_standalone_code

    source, dependencies = build_standalone_code(ROOT / "convolution/BinaryFieldConvolution.py", ROOT)
    assert not dependencies
    script = tmp_path / "main.py"
    a, b = list(range(17)), list(range(19))
    script.write_text(source + f"\nassert multiply({a}, {b}) == {naive(a, b)}\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)


def test_tiled_transform_and_product():
    import importlib
    from library_codex.benchmarks.experiments import binary_field_sixbit as reference

    trial = importlib.import_module("library_codex.convolution.BinaryFieldConvolution")

    rng = random.Random(84512)
    for height in range(2, 13):
        size = 1 << height
        constants = trial._constants(size)
        source = [trial._expand(rng.getrandbits(64)) for _ in range(size)]
        expected = source[:]
        reference._transform(expected, constants)
        for low in sorted({0, 1, height // 2, height - 1, height}):
            values = source[:]
            trial._transform(values, constants, low=low)
            for begin in range(0, size, 1 << low):
                trial._transform(values, constants, high=low, begin=begin, end=begin + (1 << low))
            assert values == expected
            for begin in range(0, size, 1 << low):
                trial._transform(values, constants, True, high=low, begin=begin, end=begin + (1 << low))
            trial._transform(values, constants, True, low=low)
            assert values == source
    for n, m in ((9, 11), (1024, 1025), (2049, 257)):
        a = [rng.getrandbits(64) for _ in range(n)]
        b = [rng.getrandbits(64) for _ in range(m)]
        assert trial.multiply(a, b) == reference.multiply(a, b)
