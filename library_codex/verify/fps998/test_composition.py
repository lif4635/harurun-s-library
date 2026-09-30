import random
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.NTT import convolution_naive
from library_codex.convolution.NTT998 import MOD
from library_codex.fps998.Composition import (
    fps_compose,
    fps_compositional_inv,
)


def _naive_compose(outer, inner, degree):
    if degree == 0:
        return []
    result = []
    for coefficient in reversed(outer[:degree]):
        result = convolution_naive(result, inner, MOD)[:degree]
        if result:
            result[0] = (result[0] + coefficient) % MOD
        else:
            result = [coefficient % MOD]
    result.extend([0] * (degree - len(result)))
    return result


def _naive_compositional_inv(series, degree):
    if degree == 0:
        return []
    result = [0] * degree
    if degree == 1:
        return result
    inverse_linear = pow(series[1] % MOD, MOD - 2, MOD)
    result[1] = inverse_linear
    for exponent in range(2, degree):
        composed = _naive_compose(series, result, exponent + 1)
        result[exponent] = -composed[exponent] * inverse_linear % MOD
    return result


def test_fps998_composition_and_compositional_inverse():
    rng = random.Random(9983)
    for _ in range(1200):
        degree = rng.randrange(1, 150)
        outer = [rng.randrange(MOD) for _ in range(rng.randrange(180))]
        inner = [rng.randrange(MOD) for _ in range(rng.randrange(180))]
        assert fps_compose(outer, inner, degree) == _naive_compose(
            outer, inner, degree
        )
    identity = [0, 1]
    for _ in range(300):
        degree = rng.randrange(2, 150)
        series = [0, rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(degree - 2)
        ]
        inverse = fps_compositional_inv(series, degree)
        expected = identity + [0] * (degree - 2)
        assert fps_compose(series, inverse, degree) == expected
        assert fps_compose(inverse, series, degree) == expected


def test_fps998_compositional_inverse_against_naive():
    rng = random.Random(20260808)
    for _ in range(200):
        degree = rng.randrange(2, 25)
        source_length = rng.randrange(2, 30)
        series = [0, rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(source_length - 2)
        ]
        assert fps_compositional_inv(series, degree) == (
            _naive_compositional_inv(series, degree)
        )


@pytest.mark.parametrize("degree", [0, 1, 2, 63, 64, 65, 127, 128, 129, 255, 256, 257])
def test_boundaries_and_input_preservation(degree):
    rng = random.Random(901 + degree)
    for constant in (0, 3, -MOD):
        outer = [rng.randrange(-MOD, 2 * MOD) for _ in range(degree + 3)]
        inner = [constant] + [rng.randrange(-MOD, 2 * MOD) for _ in range(degree + 2)]
        saved = (outer[:], inner[:])
        expected = _naive_compose(outer, inner, degree)
        assert fps_compose(outer, inner, degree) == expected
        assert fps_compose(tuple(outer), tuple(inner), degree) == expected
        assert (outer, inner) == saved


@pytest.mark.parametrize("degree", [1, 64, 65, 129, 257])
def test_shortcuts_and_zero_padding(degree):
    outer = [3, -2, MOD, 7, 1]
    for inner in ([], [0], [2], [0, 1], [0, -3], [0, 0, 5], [0, 0, 0, 7]):
        expected = _naive_compose(outer, inner, degree)
        assert fps_compose(outer, inner, degree) == expected
        assert fps_compose(outer + [MOD] * degree, inner + [-MOD] * degree, degree) == expected
    for constant in ([], [0], [-3], [MOD]):
        assert fps_compose(constant, [7, 3, 2], degree) == _naive_compose(constant, [7, 3, 2], degree)


def test_default_degree_and_nonzero_constant_contract():
    assert fps_compose([3, 2, 0, 0], [0, 1]) == [3, 2, 0, 0]
    assert fps_compose([], []) == []
    assert fps_compose([1, 2, 100], [3, 1], 2) == [7, 2]
    with pytest.raises(ValueError):
        fps_compose([1], [0, 1], -1)


def test_large_independent_recurrence():
    degree = 4097
    expected = [1, 1]
    for _ in range(2, degree):
        expected.append((expected[-1] + expected[-2]) % MOD)
    assert fps_compose([1] * degree, [0, 1, 1], degree) == expected
    outer = [(i * i - 7 * i) % MOD for i in range(65537)]
    assert fps_compose(outer, [0, 1], len(outer)) == outer
    expected = [0] * len(outer)
    power = 1
    for i in range((len(outer) + 2) // 3):
        expected[3 * i] = outer[i] * power % MOD
        power = power * 5 % MOD
    assert fps_compose(outer, [0, 0, 0, 5], len(outer)) == expected


def test_standalone_without_installed_package(tmp_path):
    from library_codex.tools.build_library_catalog import build_standalone_code

    root = Path(__file__).resolve().parents[2]
    source, _ = build_standalone_code(root / "fps998/Composition.py", root)
    assert "from library_codex." not in source
    outer = [i * i + 3 for i in range(70)]
    inner = [3, 7, 1]
    expected = _naive_compose(outer, inner, 70)
    driver = f"\nassert fps_compose({outer!r}, {inner!r}, 70) == {expected!r}\n"
    driver += "f = [0, 1, 3, 7]\ng = fps_compositional_inv(f, 70)\nassert fps_compose(f, g, 70) == [0, 1] + [0] * 68\n"
    script = tmp_path / "submission.py"
    script.write_text(source + driver, encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=20)
