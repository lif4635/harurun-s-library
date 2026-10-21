import io
import random
import types

import pytest

from library_codex.benchmarks.experiments.build_large_arithmetic_variants import MODES, PREFIX, build
from library_codex.convolution import NTT998 as ntt


@pytest.mark.parametrize("mode", MODES)
def test_variant(mode):
    module = types.ModuleType("candidate")
    exec(compile(build(mode), mode, "exec"), module.__dict__)
    forward = getattr(module, PREFIX + "butterfly8")
    inverse = getattr(module, PREFIX + "butterfly8_inv")
    multiply = getattr(module, PREFIX + "multiply_sixteen_lanes")
    rng = random.Random(22101)
    lanes = 4 if mode.startswith("four_") else 16
    for height in range(13):
        size = 1 << height
        for pattern in range(2):
            values = [rng.randrange(ntt.MOD) for _ in range(16 * size)] if pattern == 0 else [ntt.MOD - 1] * (16 * size)
            expected = values[:]
            ntt._butterfly(expected, stride=16)
            actual = values[:]
            assert forward(actual) == expected, (mode, height, "forward")
            inverse(actual)
            assert actual == [x * size % ntt.MOD for x in values], (mode, height, "inverse")
        if height <= 8:
            for n, m in ((lanes * size // 2, lanes * size // 2), (size, (lanes - 1) * size), (lanes * size, 1)):
                for pattern in range(2):
                    a = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(n)] if pattern == 0 else [ntt.MOD - 1] * n
                    b = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(m)] if pattern == 0 else [ntt.MOD - 1] * m
                    saved = a[:], b[:]
                    assert multiply(a, b, size) == ntt.multiply(a, b)
                    assert (a, b) == saved
            a = [rng.randrange(ntt.MOD) for _ in range(lanes * size // 2)]
            assert multiply(a, a, size) == ntt.multiply(a, a)
    values = [0, 1, 42, 12345678, 123456789, ntt.MOD - 1] * 31
    payload = b" \t\n".join(str(x).encode() for x in values)

    class Chunked(io.BytesIO):
        def read(self, n):
            return super().read(min(n, 17))

    for ending in (b"", b"\n", b" \r\n"):
        assert list(module.read_coefficients(Chunked(payload + ending), len(values))) == values
    assert list(module.read_coefficients(io.BytesIO(b"+12345678 "), 1)) == [12345678]
    with pytest.raises(ValueError):
        module.read_coefficients(io.BytesIO(b"1234567x9 "), 1)

    class Sized:
        def __init__(self, n):
            self.n = n

        def __len__(self):
            return self.n

    setattr(module, PREFIX + "multiply_sixteen_lanes", lambda a, b, size: size * lanes)
    dispatch = getattr(module, PREFIX + "multiply")
    assert dispatch(Sized(7729845), Sized(5653803)) == 1 << 24
    assert dispatch(Sized(1 << 24), Sized(1 << 24)) == 1 << 25


def test_reciprocal_correction():
    rng = random.Random(22102)
    mod = ntt.MOD
    for i in range(200000):
        q = rng.randrange(-8 * mod, 8 * mod)
        value = q * mod + (-1, 0, 1, mod - 1)[i & 3]
        reduced = value - (int(value * 1.0017587347173304e-09) - (value < 0)) * mod
        reduced += (reduced < 0) * mod
        reduced -= (reduced >= mod) * mod
        assert reduced == value % mod
