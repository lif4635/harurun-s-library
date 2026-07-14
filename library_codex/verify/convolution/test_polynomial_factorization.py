import random

from library_codex.convolution.FormalPowerSeries import fps_multiply
from library_codex.convolution.PolynomialFactorization import (
    factor_polynomial,
    half_gcd,
    polynomial_inverse,
)
from library_codex.convolution.PolynomialAlgorithms import polynomial_gcd


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
                    # No roots means irreducible for degrees 2 and 3; larger
                    # factors are additionally checked through reconstruction.
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
    from library_codex.convolution.FormalPowerSeries import fps_remainder
    assert fps_remainder(product, second, mod) == [1]

