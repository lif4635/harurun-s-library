import random
from math import prod
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.convolution.MultivariateMultiplication import multivariate_multiplication
from library_codex.fps.MultivariateFPS import MultivariateFPS


def test_multivariate_fps_arithmetic_and_transcendentals():
    rng = random.Random(422)
    for base in ((2, 3), (3, 3), (2, 2, 2)):
        size = 1
        for radix in base:
            size *= radix
        for _ in range(20):
            first = [rng.randrange(998244353) for _ in range(size)]
            second = [rng.randrange(998244353) for _ in range(size)]
            left = MultivariateFPS(first, base)
            right = MultivariateFPS(second, base)
            assert (left * right).f == multivariate_multiplication(
                first, second, base
            )
            first[0] = 1
            unit = MultivariateFPS(first, base)
            inverse = unit.inv()
            assert (unit * inverse).f == [1] + [0] * (size - 1)
            logarithm = unit.log()
            assert logarithm.exp().f == unit.f


def test_multivariate_indexing():
    series = MultivariateFPS(base=(2, 3, 4))
    series.set(1, 2, 3, 91)
    assert series.get(1, 2, 3) == 91
    assert series.index(1, 2, 3) == 1 + 2 * 2 + 3 * 6


def _fits(part, whole, base):
    for radix in base:
        if part % radix > whole % radix:
            return False
        part //= radix
        whole //= radix
    return True


def _multiply(first, second, base, mod):
    size = prod(base)
    return [sum(first[j] * second[i - j] for j in range(i + 1) if _fits(j, i, base)) % mod for i in range(size)]


def _inverse(series, base, mod):
    result = [pow(series[0], -1, mod)] + [0] * (len(series) - 1)
    for index in range(1, len(series)):
        result[index] = -sum(series[j] * result[index - j] for j in range(1, index + 1) if _fits(j, index, base)) * result[0] % mod
    return result


def test_dense_sparse_and_rectangular_against_naive():
    rng = random.Random(2241)
    for mod in (998244353, 101, 49):
        for base in ((), (1, 1), (1, 7), (7, 1), (3, 5), (5, 3), (4, 8), (2, 3, 4), (1, 3, 1, 2)):
            if sum(radix > 1 for radix in base) > 2 and mod != 998244353:
                continue
            size = prod(base)
            for _ in range(12):
                values = [rng.randrange(-mod, mod) if rng.randrange(3) else 0 for _ in range(size)]
                values[0] = 1
                source = MultivariateFPS(values, base, mod)
                before = source.coefficients[:]
                assert source.inverse().coefficients == _inverse(values, base, mod)
                for exponent in (-2, 0, 1, 3):
                    factor = _inverse(values, base, mod) if exponent < 0 else values
                    expected = [1] + [0] * (size - 1)
                    for _ in range(abs(exponent)):
                        expected = _multiply(expected, factor, base, mod)
                    assert source.power(exponent).coefficients == expected
                assert source.coefficients == before
                if mod == 49 and size > 7:
                    with pytest.raises(ValueError):
                        source.logarithm()
                    continue
                values[0] = 0
                zero = MultivariateFPS(values, base, mod)
                expected = [1] + [0] * (size - 1)
                power = expected[:]
                factorial = 1
                for exponent in range(1, 1 + sum(radix - 1 for radix in base)):
                    power = _multiply(power, values, base, mod)
                    factorial = factorial * exponent % mod
                    inverse_factorial = pow(factorial, -1, mod)
                    expected = [(a + b * inverse_factorial) % mod for a, b in zip(expected, power)]
                actual = zero.exponential()
                assert actual.coefficients == expected
                assert actual.logarithm().coefficients == zero.coefficients


def test_sparse_threshold_and_zero_constant_power():
    rng = random.Random(522)
    base = (7, 9)
    for count in (0, 1, 16, 17):
        values = [1] + [0] * 62
        for index in rng.sample(range(1, 63), count):
            values[index] = rng.randrange(998244353)
        source = MultivariateFPS(values, base)
        assert source.inverse().coefficients == _inverse(values, base, 998244353)
        assert source.power(3).coefficients == _multiply(_multiply(values, values, base, 998244353), values, base, 998244353)
        values[0] = 0
        source = MultivariateFPS(values, base)
        assert source.power(3).coefficients == _multiply(_multiply(values, values, base, 998244353), values, base, 998244353)
        assert source.exponential().logarithm().coefficients == values


def test_large_sparse_bivariate_inverse():
    from math import comb

    width, height = 256, 256
    values = [0] * (width * height)
    values[0], values[1], values[width] = 1, -1, -1
    actual = MultivariateFPS(values, (width, height)).inverse().coefficients
    for x, y in ((0, 0), (255, 0), (0, 255), (255, 255), (79, 131)):
        assert actual[x + width * y] == comb(x + y, x) % 998244353


def test_large_integer_power_and_sparse_logarithm():
    rng = random.Random(5423)
    mod = 998244353
    for base in ((1, 35), (35, 1), (5, 7), (3, 3, 3)):
        size = prod(base)
        for count in (1, 8, 16, size - 1):
            values = [5] + [0] * (size - 1)
            for index in rng.sample(range(1, size), count):
                values[index] = rng.randrange(1, mod)
            source = MultivariateFPS(values, base)
            for exponent in (-17, 9, 18):
                factor = _inverse(values, base, mod) if exponent < 0 else values
                expected = [1] + [0] * (size - 1)
                for _ in range(abs(exponent)):
                    expected = _multiply(expected, factor, base, mod)
                assert source.power(exponent).coefficients == expected
            values[0] = 1
            source = MultivariateFPS(values, base)
            derivative = [i * value % mod for i, value in enumerate(values)]
            expected = _multiply(derivative, _inverse(values, base, mod), base, mod)
            expected[1:] = [value * pow(i, -1, mod) % mod for i, value in enumerate(expected[1:], 1)]
            assert source.logarithm().coefficients == expected


def test_validation_and_standalone(tmp_path):
    from library_codex.tools.build_library_catalog import build_standalone_code

    with pytest.raises(ValueError):
        MultivariateFPS([1], (0,))
    with pytest.raises(ValueError):
        MultivariateFPS([1], (2, 3))
    with pytest.raises(ZeroDivisionError):
        MultivariateFPS([0, 1], (2, 1)).power(-1)
    root = Path(__file__).resolve().parents[2]
    source, _ = build_standalone_code(root / "fps/MultivariateFPS.py", root)
    path = tmp_path / "submission.py"
    driver = '\nf = MultivariateFormalPowerSeries([1, -1, -1, 0], (2, 2))\nassert f.inverse().coefficients == [1, 1, 1, 2]\nassert f.logarithm().exponential().coefficients == f.coefficients\n'
    driver += '\nf = MultivariateFormalPowerSeries([1] * 323, (17, 19))\ng = f.inverse().coefficients\nassert [(i, x) for i, x in enumerate(g) if x] == [(0, 1), (1, 998244352), (17, 998244352), (18, 1)]\n'
    path.write_text(source + driver, encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(path)], cwd=tmp_path, check=True, timeout=30)


def test_article_examples_and_weighted_derivative():
    source = MultivariateFPS([1, -1, -1, 0], (2, 2))
    assert source.inverse().coefficients == [1, 1, 1, 2]
    assert MultivariateFPS([0, 1, 1, 0], (2, 2)).power(2).coefficients == [0, 0, 0, 2]
    source = MultivariateFPS([7, 11, 13, 17, 19, 23], (2, 3))
    assert source.derivative().coefficients == [0, 11, 26, 51, 76, 115]
    assert source.derivative().integral().coefficients == [0, 11, 13, 17, 19, 23]
    assert source.integral().coefficients[0] == 7
    with pytest.raises(ValueError):
        source.logarithm()
    with pytest.raises(ValueError):
        source.exponential()


def test_large_sparse_exp_log_known_coefficients():
    from math import comb, factorial

    mod = 998244353
    width, height = 127, 133
    coefficients = [0] * (width * height)
    coefficients[1] = coefficients[width] = 1
    exponential = MultivariateFPS(coefficients, (width, height)).exponential().coefficients
    coefficients[0] = 1
    coefficients[1] = coefficients[width] = -1
    logarithm = MultivariateFPS(coefficients, (width, height)).logarithm().coefficients
    for x, y in ((0, 1), (1, 0), (126, 0), (0, 132), (126, 132), (43, 83)):
        assert exponential[x + width * y] == pow(factorial(x) * factorial(y), -1, mod)
        assert logarithm[x + width * y] == -comb(x + y, x) * pow(x + y, -1, mod) % mod


def test_colored_inverse_prefix_against_naive():
    from library_codex.fps.MultivariateFPS import _inverse_prefix

    rng = random.Random(93010)
    mod = 998244353
    for base in ((17, 19), (19, 17), (2, 257), (257, 2), (1, 513), (513, 1)):
        values = [rng.randrange(mod) for _ in range(prod(base))]
        values[0] = 7
        expected = _inverse(values, base, mod)
        for size in (255, 256, 257, len(values)):
            assert _inverse_prefix(values, base, mod, size) == expected[:size]
            short = values[:size // 2]
            padded = short + [0] * (len(values) - len(short))
            assert _inverse_prefix(short, base, mod, size) == _inverse(padded, base, mod)[:size]


def test_sparse_dispatch_boundaries():
    from library_codex.fps.MultivariateFPS import _sparse_2d, _inverse_prefix, _log_prefix, _exp_prefix, _inverses

    mod = 998244353
    rng = random.Random(93011)
    for base, inverse_limit, other_limit in (((8, 8), 16, 16), ((32, 32), 64, 128)):
        size = prod(base)
        for exponent, logarithm, limit in ((-1, False, inverse_limit), (None, True, other_limit),
                                           (None, False, other_limit), (3, False, other_limit)):
            for count in (limit, limit + 1):
                values = [0 if exponent is None and not logarithm else 1] + [0] * (size - 1)
                for i in rng.sample(range(1, size), count):
                    values[i] = rng.randrange(1, mod)
                result = _sparse_2d(values, base, mod, exponent, logarithm)
                if count > limit:
                    assert result is None
                else:
                    if logarithm:
                        expected = _log_prefix(values, base, mod, size, _inverses(size, mod))
                    elif exponent is None:
                        expected = _exp_prefix(values, base, mod, size)
                    elif exponent == -1:
                        expected = _inverse_prefix(values, base, mod, size)
                    else:
                        expected = multivariate_multiplication(values, values, base, mod)
                        expected = multivariate_multiplication(expected, values, base, mod)
                    assert result == expected
