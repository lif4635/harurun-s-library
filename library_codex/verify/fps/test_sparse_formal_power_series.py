import math
from pathlib import Path
import random
import subprocess
import sys

import pytest

from library_codex.fps.FormalPowerSeries import fps_exponential, fps_inverse, fps_logarithm, fps_multiply, fps_power
from library_codex.fps.SparseFormalPowerSeries import sparse_divide, sparse_exponential, sparse_inverse, sparse_logarithm, sparse_power
from library_codex.tools.build_library_catalog import build_standalone_code


MOD = 998244353


def _multiply(first, second, degree, mod):
    result = [0] * degree
    for i, a in enumerate(first[:degree]):
        for j, b in enumerate(second[:degree - i]):
            result[i + j] = (result[i + j] + a * b) % mod
    return result


def _inverse(series, degree, mod):
    result = [0] * degree
    result[0] = pow(series[0], -1, mod)
    for i in range(1, degree):
        result[i] = -sum(series[j] * result[i - j] for j in range(1, min(i + 1, len(series)))) * result[0] % mod
    return result


def test_sparse_operations_against_dense_fps():
    rng = random.Random(31)
    for degree in (1, 2, 20, 100):
        series = [0] * degree
        series[0] = 1
        for _ in range(max(1, degree // 8)):
            series[rng.randrange(degree)] = rng.randrange(MOD)
        series[0] = 1
        numerator = [rng.randrange(MOD) for _ in range(degree)]
        assert sparse_inverse(series, degree) == fps_inverse(series, degree)
        assert sparse_divide(numerator, series, degree) == fps_multiply(numerator, fps_inverse(series, degree))[:degree]
        logarithm = sparse_logarithm(series, degree)
        assert logarithm == fps_logarithm(series, degree)
        assert sparse_exponential(logarithm, degree) == fps_exponential(logarithm, degree)
        assert sparse_power(series, 7, degree) == fps_power(series, 7, degree)


def test_power_against_repeated_naive_products():
    rng = random.Random(941)
    for mod in (101, MOD, 49, 143):
        for _ in range(200):
            degree = rng.randrange(1, 7)
            series = [rng.randrange(-mod, mod * 2) if rng.randrange(3) == 0 else 0 for _ in range(rng.randrange(1, 12))]
            exponent = rng.randrange(-5, 7)
            leading = next((value for value in series if value % mod), 0)
            if exponent < 0 and math.gcd(series[0], mod) != 1:
                continue
            if exponent > 0 and leading and math.gcd(leading, mod) != 1:
                continue
            factor = _inverse(series, degree, mod) if exponent < 0 else series
            expected = [1] + [0] * (degree - 1)
            for _ in range(abs(exponent)):
                expected = _multiply(expected, factor, degree, mod)
            assert sparse_power(tuple(series), exponent, degree, mod) == expected


def test_exp_log_with_composite_modulus():
    for mod in (49, 143, MOD):
        series = [0, 3, 0, 2, 0, 5]
        expected = [1, 0, 0, 0, 0, 0]
        power = expected[:]
        factorial = 1
        for exponent in range(1, 6):
            factorial = factorial * exponent % mod
            power = _multiply(power, series, 6, mod)
            expected = [(a + b * pow(factorial, -1, mod)) % mod for a, b in zip(expected, power)]
        assert sparse_exponential(series, mod=mod) == expected
        assert sparse_logarithm(expected, mod=mod) == series
    for function, args in ((sparse_exponential, ([0, 1],)), (sparse_logarithm, ([1, 1],)), (sparse_power, ([1, 1], 2))):
        with pytest.raises(ValueError):
            function(*args, degree=8, mod=49)


def test_empty_invalid_and_truncation():
    for function, args in ((sparse_inverse, ([1],)), (sparse_divide, ([1], [1])), (sparse_exponential, ([0],)), (sparse_logarithm, ([1],)), (sparse_power, ([1], -2))):
        assert function(*args, degree=0) == []
        with pytest.raises(ValueError):
            function(*args, degree=-1)
    assert sparse_power([], 0, 0) == []
    assert sparse_power([], 0, 3) == [1, 0, 0]
    assert sparse_power([0, 0, 3], 2, 5) == [0, 0, 0, 0, 9]
    assert sparse_power([0, 0, 3], 2, 4) == [0] * 4
    for series in ([], [0], [0, 1]):
        with pytest.raises(ZeroDivisionError):
            sparse_power(series, -1, 5)
    assert sparse_power([2, MOD, MOD * 2], -2, 10) == [pow(4, -1, MOD)] + [0] * 9


def test_large_sparse_negative_power():
    degree = 131072
    expected = list(range(1, degree + 1))
    assert sparse_power([1, -1], -2, degree) == expected


def test_standalone(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source, dependencies = build_standalone_code(root / "fps/SparseFormalPowerSeries.py", root)
    assert not dependencies
    path = tmp_path / "submission.py"
    path.write_text(source + '\nassert sparse_power([1, -1], -2, 100) == list(range(1, 101))\n', encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(path)], check=True, cwd=tmp_path, timeout=30)
