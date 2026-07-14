import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.FormalPowerSeries import (
    fps_add,
    fps_derivative,
    fps_divmod,
    fps_evaluate,
    fps_exponential,
    fps_integral,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_negate,
    fps_power,
    fps_product,
    fps_quotient,
    fps_remainder,
    fps_subtract,
    fps_taylor_shift,
)
from library_codex.convolution.NTT import convolution_naive


MOD = 998244353


def naive_inverse(series, degree, mod):
    result = [pow(series[0], -1, mod)]
    for index in range(1, degree):
        value = 0
        for offset in range(1, min(index + 1, len(series))):
            value += series[offset] * result[index - offset]
        result.append(-value * result[0] % mod)
    return result


def naive_exponential(series, degree, mod):
    result = [1]
    for index in range(1, degree):
        value = 0
        for offset in range(1, index + 1):
            if offset < len(series):
                value += offset * series[offset] * result[index - offset]
        result.append(value * pow(index, -1, mod) % mod)
    return result


def test_basic_operations_against_naive():
    rng = random.Random(0)
    for _ in range(5000):
        first = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(35))]
        second = [rng.randrange(-MOD, MOD) for _ in range(rng.randrange(35))]
        size = max(len(first), len(second))
        expected_add = [
            (
                (first[index] if index < len(first) else 0)
                + (second[index] if index < len(second) else 0)
            ) % MOD
            for index in range(size)
        ]
        expected_subtract = [
            (
                (first[index] if index < len(first) else 0)
                - (second[index] if index < len(second) else 0)
            ) % MOD
            for index in range(size)
        ]
        assert fps_add(first, second) == expected_add
        assert fps_subtract(first, second) == expected_subtract
        assert fps_negate(first) == [-value % MOD for value in first]
        assert fps_multiply(first, second) == convolution_naive(
            first, second, MOD
        )
        assert fps_derivative(first) == [
            index * first[index] % MOD for index in range(1, len(first))
        ]
        assert fps_derivative(fps_integral(first)) == [
            value % MOD for value in first
        ]
        value = rng.randrange(MOD)
        expected = 0
        power = 1
        for coefficient in first:
            expected = (expected + coefficient * power) % MOD
            power = power * value % MOD
        assert fps_evaluate(first, value) == expected


def test_inverse_log_exp_against_quadratic_formulas():
    rng = random.Random(1)
    for _ in range(1500):
        degree = rng.randrange(1, 150)
        series = [rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(rng.randrange(150))
        ]
        inverse = fps_inverse(series, degree)
        assert inverse == naive_inverse(series, degree, MOD)
        product = fps_multiply(series, inverse)[:degree]
        assert product == [1] + [0] * (degree - 1)

        exponential_source = [0] + [
            rng.randrange(MOD) for _ in range(rng.randrange(149))
        ]
        exponential = fps_exponential(exponential_source, degree)
        assert exponential == naive_exponential(
            exponential_source, degree, MOD
        )
        assert fps_logarithm(exponential, degree) == [
            exponential_source[index] % MOD
            if index < len(exponential_source) else 0
            for index in range(degree)
        ]


def test_power_division_taylor_shift_and_product():
    rng = random.Random(2)
    for _ in range(2000):
        degree = rng.randrange(1, 80)
        series = [rng.randrange(MOD) for _ in range(rng.randrange(40))]
        exponent = rng.randrange(7)
        expected = [1]
        for _ in range(exponent):
            expected = convolution_naive(expected, series, MOD)[:degree]
        expected.extend([0] * (degree - len(expected)))
        assert fps_power(series, exponent, degree) == expected

        divisor = [rng.randrange(MOD) for _ in range(rng.randrange(1, 30))]
        if divisor[-1] == 0:
            divisor[-1] = 1
        quotient = [rng.randrange(MOD) for _ in range(rng.randrange(30))]
        remainder = [
            rng.randrange(MOD) for _ in range(rng.randrange(len(divisor)))
        ]
        dividend = fps_add(fps_multiply(quotient, divisor), remainder)
        expected_quotient, expected_remainder = fps_divmod(dividend, divisor)
        while quotient and quotient[-1] == 0:
            quotient.pop()
        while remainder and remainder[-1] == 0:
            remainder.pop()
        assert expected_quotient == quotient
        assert expected_remainder == remainder
        assert fps_quotient(dividend, divisor) == quotient
        assert fps_remainder(dividend, divisor) == remainder

        shift = rng.randrange(MOD)
        shifted = fps_taylor_shift(series, shift)
        point = rng.randrange(MOD)
        assert fps_evaluate(shifted, point) == fps_evaluate(
            series, point + shift
        )

    polynomials = [[1, index] for index in range(1, 100)]
    expected = [1]
    for polynomial in polynomials:
        expected = convolution_naive(expected, polynomial, MOD)
    assert fps_product(polynomials) == expected
    assert fps_product([]) == [1]
    assert fps_product([[1], []]) == []

    divisor = [rng.randrange(MOD) for _ in range(100)]
    divisor[-1] = 1
    quotient = [rng.randrange(MOD) for _ in range(120)]
    remainder = [rng.randrange(MOD) for _ in range(99)]
    dividend = fps_add(fps_multiply(quotient, divisor), remainder)
    assert fps_divmod(dividend, divisor) == (quotient, remainder)


def test_other_prime_fallback():
    mod = 10**9 + 7
    rng = random.Random(3)
    degree = 220
    series = [rng.randrange(1, mod)] + [
        rng.randrange(mod) for _ in range(degree - 1)
    ]
    assert fps_inverse(series, degree, mod) == naive_inverse(
        series, degree, mod
    )
    source = [0] + [rng.randrange(mod) for _ in range(degree - 1)]
    assert fps_exponential(source, degree, mod) == naive_exponential(
        source, degree, mod
    )

    for friendly_mod in (924844033, 1012924417):
        source = [0] + [rng.randrange(friendly_mod) for _ in range(300)]
        assert fps_exponential(source, 301, friendly_mod) == naive_exponential(
            source, 301, friendly_mod
        )


def test_validation_and_negative_power():
    with pytest.raises(ZeroDivisionError):
        fps_inverse([0], 1)
    with pytest.raises(ValueError):
        fps_logarithm([2], 1)
    with pytest.raises(ValueError):
        fps_exponential([1], 1)
    with pytest.raises(ZeroDivisionError):
        fps_divmod([1], [])
    with pytest.raises(ValueError):
        fps_power([0, 1], -1, 5)
    series = [2, 3, 4, 5]
    inverse = fps_inverse(series, 20)
    assert fps_power(series, -1, 20) == inverse


def test_large_without_recursion():
    degree = 100000
    series = [1] + [index * index % MOD for index in range(1, degree)]
    inverse = fps_inverse(series, degree)
    assert len(inverse) == degree
    assert fps_multiply(series, inverse)[:20] == [1] + [0] * 19
    source = [0] + [index % 1000 for index in range(1, degree)]
    exponential = fps_exponential(source, degree)
    assert len(exponential) == degree
    assert fps_logarithm(exponential, 1000) == source[:1000]


if __name__ == "__main__":
    test_basic_operations_against_naive()
    test_inverse_log_exp_against_quadratic_formulas()
    test_power_division_taylor_shift_and_product()
    test_other_prime_fallback()
    test_validation_and_negative_power()
    test_large_without_recursion()
