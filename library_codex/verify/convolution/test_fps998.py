import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.NTT import convolution_naive
from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.FPS import (
    fps_add,
    fps_diff,
    fps_div,
    fps_eval,
    fps_exp,
    fps_integral,
    fps_inv,
    fps_log,
    fps_neg,
    fps_pow,
    fps_product,
    fps_sqrt,
    fps_sub,
    shrink,
    taylor_shift,
)
from library_codex.polynomial.PolynomialDivision998 import (
    poly_div,
    poly_divmod,
    poly_mod,
)
from library_codex.fps998.Composition import (
    fps_compose,
    fps_compositional_inv,
)


def _naive_inverse(series, degree):
    result = [pow(series[0], MOD - 2, MOD)]
    for index in range(1, degree):
        value = 0
        for offset in range(1, min(index + 1, len(series))):
            value += series[offset] * result[index - offset]
        result.append(-value * result[0] % MOD)
    return result


def _naive_exponential(series, degree):
    result = [1]
    for index in range(1, degree):
        value = 0
        for offset in range(1, index + 1):
            if offset < len(series):
                value += offset * series[offset] * result[index - offset]
        result.append(value * pow(index, MOD - 2, MOD) % MOD)
    return result


def _naive_compose(outer, inner, degree):
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


def test_fps998_basic_operations_against_naive():
    rng = random.Random(9980)
    for _ in range(3000):
        first = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(35))]
        second = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(35))]
        size = max(len(first), len(second))
        assert fps_add(first, second) == [
            ((first[i] if i < len(first) else 0)
             + (second[i] if i < len(second) else 0)) % MOD
            for i in range(size)
        ]
        assert fps_sub(first, second) == [
            ((first[i] if i < len(first) else 0)
             - (second[i] if i < len(second) else 0)) % MOD
            for i in range(size)
        ]
        assert fps_neg(first) == [-value % MOD for value in first]
        assert fps_diff(first) == [
            index * first[index] % MOD for index in range(1, len(first))
        ]
        assert fps_diff(fps_integral(first)) == [value % MOD for value in first]
        value = rng.randrange(MOD)
        assert fps_eval(first, value) == sum(
            coefficient * pow(value, index, MOD)
            for index, coefficient in enumerate(first)
        ) % MOD
        assert shrink(first + [0, MOD]) == shrink(first)


def test_fps998_inverse_log_and_exp_against_naive():
    rng = random.Random(9981)
    for _ in range(800):
        degree = rng.randrange(1, 130)
        series = [rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(rng.randrange(130))
        ]
        assert fps_inv(series, degree) == _naive_inverse(series, degree)
        source = [0] + [rng.randrange(MOD) for _ in range(rng.randrange(129))]
        exponential = fps_exp(source, degree)
        assert exponential == _naive_exponential(source, degree)
        assert fps_log(exponential, degree) == [
            source[index] % MOD if index < len(source) else 0
            for index in range(degree)
        ]


def test_fps998_power_sqrt_division_shift_and_product():
    rng = random.Random(9982)
    for _ in range(1000):
        degree = rng.randrange(1, 70)
        series = [rng.randrange(MOD) for _ in range(rng.randrange(35))]
        exponent = rng.randrange(7)
        expected = [1]
        for _ in range(exponent):
            expected = convolution_naive(expected, series, MOD)[:degree]
        expected.extend([0] * (degree - len(expected)))
        assert fps_pow(series, exponent, degree) == expected

        root = [rng.randrange(MOD) for _ in range(rng.randrange(1, 25))]
        squared = multiply(root, root)[:degree]
        actual_root = fps_sqrt(squared, degree)
        assert actual_root is not None
        assert multiply(actual_root, actual_root)[:degree] == (
            squared + [0] * degree
        )[:degree]

        divisor = [rng.randrange(MOD) for _ in range(rng.randrange(1, 25))]
        divisor[-1] = divisor[-1] or 1
        quotient = [rng.randrange(MOD) for _ in range(rng.randrange(25))]
        remainder = [rng.randrange(MOD) for _ in range(rng.randrange(len(divisor)))]
        dividend = fps_add(multiply(quotient, divisor), remainder)
        while quotient and quotient[-1] == 0:
            quotient.pop()
        while remainder and remainder[-1] == 0:
            remainder.pop()
        assert poly_divmod(dividend, divisor) == (quotient, remainder)
        assert poly_div(dividend, divisor) == quotient
        assert poly_mod(dividend, divisor) == remainder

        denominator = [rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(rng.randrange(20))
        ]
        numerator = [rng.randrange(MOD) for _ in range(rng.randrange(20))]
        formal_quotient = fps_div(numerator, denominator, degree)
        expected_numerator = [value % MOD for value in numerator[:degree]]
        expected_numerator.extend([0] * (degree - len(expected_numerator)))
        assert len(formal_quotient) == degree
        assert multiply(formal_quotient, denominator)[:degree] == expected_numerator

        shift = rng.randrange(MOD)
        point = rng.randrange(MOD)
        assert fps_eval(taylor_shift(series, shift), point) == fps_eval(
            series, point + shift
        )

    polynomials = [[1, index] for index in range(1, 80)]
    expected = [1]
    for polynomial in polynomials:
        expected = convolution_naive(expected, polynomial, MOD)
    assert fps_product(polynomials) == expected

    divisor = [rng.randrange(MOD) for _ in range(100)]
    divisor[-1] = 1
    quotient = [rng.randrange(MOD) for _ in range(120)]
    remainder = [rng.randrange(MOD) for _ in range(99)]
    dividend = fps_add(multiply(quotient, divisor), remainder)
    assert poly_divmod(dividend, divisor) == (quotient, remainder)


def test_fps998_validation_and_large_input():
    with pytest.raises(ZeroDivisionError):
        fps_inv([0], 1)
    with pytest.raises(ValueError):
        fps_log([2], 1)
    with pytest.raises(ValueError):
        fps_exp([1], 1)
    with pytest.raises(ZeroDivisionError):
        poly_divmod([1], [])
    with pytest.raises(ZeroDivisionError):
        fps_div([1], [0], 1)

    degree = 50000
    series = [1] + [index * index % MOD for index in range(1, degree)]
    inverse = fps_inv(series, degree)
    assert len(inverse) == degree
    assert multiply(series, inverse)[:20] == [1] + [0] * 19


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


def test_fps998_sparse_large_relations():
    degree = 4096
    unit = [0] * degree
    unit[0] = 1
    for index in (1, 3, 17, 65, 257, 1025):
        unit[index] = (index * index + 13) % MOD

    inverse = fps_inv(unit, degree)
    assert multiply(unit, inverse)[:degree] == [1] + [0] * (degree - 1)

    logarithm = fps_log(unit, degree)
    assert fps_exp(logarithm, degree) == unit

    exponent = 123456789
    powered = fps_pow(unit, exponent, degree)
    assert fps_log(powered, degree) == [
        value * exponent % MOD for value in logarithm
    ]


if __name__ == "__main__":
    test_fps998_basic_operations_against_naive()
    test_fps998_inverse_log_and_exp_against_naive()
    test_fps998_power_sqrt_division_shift_and_product()
    test_fps998_validation_and_large_input()
    test_fps998_composition_and_compositional_inverse()
