import random
from itertools import product

import pytest

from library_codex.fps.FormalPowerSeries import fps_multiply
from library_codex.polynomial.PolynomialFactorization import (
    factor_polynomial,
    half_gcd,
    polynomial_inverse,
)
from library_codex.polynomial.PolynomialGCD import polynomial_gcd


def test_polynomial_factorization_reconstructs_input():
    rng = random.Random(867)
    for mod in (2, 3, 5, 17, 998244353):
        for _ in range(100):
            roots = [rng.randrange(mod) for _ in range(rng.randrange(1, 14))]
            polynomial = [1]
            for root in roots:
                polynomial = fps_multiply(polynomial, [-root % mod, 1], mod)
            factors = factor_polynomial(polynomial, mod)
            reconstructed = [1]
            for factor in factors:
                reconstructed = fps_multiply(reconstructed, factor, mod)
                if len(factor) > 2:
                    if len(factor) <= 4:
                        assert all(
                            sum(coefficient * pow(value, index, mod)
                                for index, coefficient in enumerate(factor)) % mod
                            for value in range(mod)
                        )
            assert reconstructed == polynomial


def test_half_gcd_and_polynomial_inverse():
    mod = 998244353
    first = [1, 3, 5, 7, 9]
    second = [2, 4, 6, 8]
    assert half_gcd(first, second, mod) == polynomial_gcd(first, second, mod)
    ok, inverse = polynomial_inverse(first, second, mod)
    assert ok
    product = fps_multiply(first, inverse, mod)
    from library_codex.polynomial.PolynomialDivision import poly_mod
    assert poly_mod(product, second, mod) == [1]


def test_binary_equal_degree_factors():
    irreducibles = ([1, 1, 0, 0, 1], [1, 0, 0, 1, 1], [1, 1, 1, 1, 1])
    for first in range(3):
        for second in range(first + 1, 3):
            polynomial = fps_multiply(irreducibles[first], irreducibles[second], 2)
            expected = sorted([irreducibles[first], irreducibles[second]])
            for seed in range(4):
                assert factor_polynomial(polynomial, 2, seed) == expected


def test_small_fields_against_trial_division():
    def divide(first, second, mod):
        remainder = first[:]
        quotient = [0] * max(0, len(first) - len(second) + 1)
        for index in range(len(quotient) - 1, -1, -1):
            value = remainder[index + len(second) - 1]
            quotient[index] = value
            for offset, coefficient in enumerate(second):
                remainder[index + offset] = (remainder[index + offset] - value * coefficient) % mod
        while remainder and not remainder[-1]:
            remainder.pop()
        return quotient, remainder

    for mod, maximum in ((2, 8), (3, 5)):
        irreducibles = []
        for degree in range(1, maximum + 1):
            for coefficients in product(range(mod), repeat=degree):
                polynomial = list(coefficients) + [1]
                remaining = polynomial
                expected = []
                for divisor in irreducibles:
                    while len(remaining) >= len(divisor):
                        quotient, remainder = divide(remaining, divisor, mod)
                        if remainder:
                            break
                        expected.append(divisor)
                        remaining = quotient
                if len(remaining) > 1:
                    expected.append(remaining)
                    irreducibles.append(remaining)
                expected.sort(key=lambda factor: (len(factor), factor))
                assert factor_polynomial(polynomial, mod) == expected


def test_factorization_boundary_values():
    assert factor_polynomial([2, 0, 4, 1], 5) == [[1, 1], [1, 1], [2, 1]]
    assert factor_polynomial([3, 0], 5) == [[3]]
    assert factor_polynomial([0, 0, 2], 5) == [[0, 1], [0, 1]]
    with pytest.raises(ValueError):
        factor_polynomial([], 5)
    with pytest.raises(ValueError):
        factor_polynomial([0, 5], 5)
