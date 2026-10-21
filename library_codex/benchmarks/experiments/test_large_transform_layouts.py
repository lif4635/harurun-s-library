import random
import types

import pytest

from library_codex.benchmarks.experiments.build_large_transform_variants import PREFIX, build
from library_codex.convolution import NTT998 as ntt


def test_frozen_source_and_initial_screen(tmp_path, monkeypatch):
    from library_codex.benchmarks.experiments import build_large_transform_variants as variants

    expected = variants.baseline_data()
    path = tmp_path / "baseline.py"
    path.write_bytes(expected.replace(b"\n", b"\r\n"))
    monkeypatch.setattr(variants, "BASE", path)
    assert variants.baseline_data() == expected
    assert variants.initial_screen_source()


@pytest.mark.parametrize("lanes,tile_bits,zero,cached,fused", [
    (8, None, False, False, False),
    (16, None, False, False, False),
    (32, None, False, False, False),
    (16, 3, False, False, False),
    (16, 6, False, False, False),
    (16, 9, False, False, False),
    (8, None, True, False, False),
    (16, None, True, False, False),
    (16, 3, False, True, False),
    (16, 3, False, True, True),
    (16, 3, True, True, False),
])
def test_layout(lanes, tile_bits, zero, cached, fused):
    module = types.ModuleType("candidate")
    exec(compile(build(lanes, tile_bits, zero, cached, fused), "candidate", "exec"), module.__dict__)
    forward = getattr(module, PREFIX + "butterfly8")
    inverse = getattr(module, PREFIX + "butterfly8_inv")
    multiply = getattr(module, PREFIX + "multiply_sixteen_lanes")
    rng = random.Random(22001)
    for height in range(14):
        size = 1 << height
        values = [rng.randrange(ntt.MOD) for _ in range(lanes * size)]
        expected = values[:]
        ntt._butterfly(expected, stride=lanes)
        actual = values[:]
        assert forward(actual, lanes) == expected, (height, "forward")
        inverse(actual, lanes)
        assert actual == [x * size % ntt.MOD for x in values], (height, "inverse")
        if height <= 8:
            for pattern in range(3):
                n = rng.randrange(1, lanes * size)
                m = lanes * size - n + 1
                a = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(n)]
                b = [rng.randrange(-ntt.MOD, 2 * ntt.MOD) for _ in range(m)]
                if pattern == 0:
                    a, b = [ntt.MOD - 1] * n, [ntt.MOD - 1] * m
                saved = a[:], b[:]
                assert multiply(a, b, size) == ntt.multiply(a, b)
                assert (a, b) == saved
            a = [rng.randrange(ntt.MOD) for _ in range(lanes * size // 2)]
            assert multiply(a, a, size) == ntt.multiply(a, a)
    class Sized:
        def __init__(self, n):
            self.n = n

        def __len__(self):
            return self.n

    setattr(module, PREFIX + "multiply_sixteen_lanes", lambda a, b, size: size * lanes)
    public = getattr(module, PREFIX + "multiply")
    assert public(Sized(7729845), Sized(5653803)) == 1 << 24
    assert public(Sized(1 << 24), Sized(1 << 24)) == 1 << 25
