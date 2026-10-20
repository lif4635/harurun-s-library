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


def test_standalone(tmp_path):
    from library_codex.tools.build_library_catalog import ROOT, build_standalone_code

    source, dependencies = build_standalone_code(ROOT / "convolution/BinaryFieldConvolution.py", ROOT)
    assert not dependencies
    script = tmp_path / "main.py"
    a, b = list(range(17)), list(range(19))
    script.write_text(source + f"\nassert multiply({a}, {b}) == {naive(a, b)}\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)
