import random
import types

import pytest

from library_codex.benchmarks.experiments.build_large_locality_variants import MODES, PREFIX, build
from library_codex.convolution.NTT998 import MOD, multiply


@pytest.mark.parametrize("mode", MODES)
def test_locality_variant(mode):
    module = types.ModuleType("candidate")
    exec(compile(build(mode), mode, "exec"), module.__dict__)
    candidate = getattr(module, PREFIX + "multiply_sixteen_lanes")
    rng = random.Random(241024)
    for height in (0, 3, 5, 6, 7, 9, 12, 13, 14):
        size = 1 << height
        for n, m in ((8 * size, 8 * size), (16 * size, 1), (3 * size, 11 * size)):
            a = [rng.randrange(-MOD, 2 * MOD) for _ in range(n)]
            b = [rng.randrange(-MOD, 2 * MOD) for _ in range(m)]
            saved = a[:], b[:]
            result = candidate(a, b, size)
            assert isinstance(result, list)
            assert result == multiply(a, b), (mode, height, n, m)
            assert (a, b) == saved
        a = [MOD - 1] * (8 * size)
        assert candidate(a, a, size) == multiply(a, a)
