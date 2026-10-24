import random
import types
from io import BytesIO

import pytest

from library_codex.benchmarks.experiments.build_large_layout_variants import MODES, PREFIX, build
from library_codex.convolution.NTT998 import MOD, multiply


@pytest.mark.parametrize("mode", MODES)
def test_layout_variant(mode):
    module = types.ModuleType("candidate")
    exec(compile(build(mode), mode, "exec"), module.__dict__)
    candidate = getattr(module, PREFIX + "multiply_sixteen_lanes")
    rng = random.Random(251025)
    for height in (2, 3, 4, 5, 6, 9, 11, 12):
        size = 1 << height
        for n, m in ((8 * size, 8 * size), (16 * size, 1), (3 * size, 11 * size), (1, 1)):
            a = [rng.randrange(-MOD, 2 * MOD) for _ in range(n)]
            b = [rng.randrange(-MOD, 2 * MOD) for _ in range(m)]
            saved = a[:], b[:]
            result = candidate(a, b, size)
            assert isinstance(result, list)
            assert result == multiply(a, b), (mode, height, n, m)
            assert (a, b) == saved
        a = [MOD - 1] * (8 * size)
        saved = a[:]
        assert candidate(a, a, size) == multiply(a, a), (mode, height, "square")
        assert a == saved


@pytest.mark.parametrize("mode", ("current", "input_text", "input_digits"))
def test_layout_reader(mode):
    module = types.ModuleType("reader")
    exec(compile(build(mode), mode, "exec"), module.__dict__)
    values = [0, 1, MOD - 1, 37, 123456789] * 16000
    for ending in (b"", b"\n", b" \r\n"):
        data = b" \t\n".join(str(value).encode() for value in values) + ending
        assert list(module.read_coefficients(BytesIO(data), len(values))) == values


def test_layout_digit_reader_rejects_invalid_input():
    module = types.ModuleType("reader")
    exec(compile(build("input_digits"), "input_digits", "exec"), module.__dict__)
    for data in (b"1", b"1 2 3", b"1 a", b"1 -2"):
        with pytest.raises(ValueError):
            module.read_coefficients(BytesIO(data), 2)
