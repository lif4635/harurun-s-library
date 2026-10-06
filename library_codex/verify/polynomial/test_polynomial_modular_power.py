import random

import pytest

from library_codex.fps.FormalPowerSeries import fps_multiply
from library_codex.polynomial.PolynomialDivision import poly_mod
from library_codex.polynomial.PolynomialModularPower import polynomial_inverse_mod, polynomial_pow_mod


def test_power_against_repeated_multiplication():
    rng = random.Random(51005)
    for mod in (2, 17, 998244353):
        for degree in (1, 2, 3, 62, 63, 64, 65, 127, 128):
            modulus = [rng.randrange(mod) for _ in range(degree)] + [rng.randrange(1, mod)]
            for size in (0, 1, degree, degree * 2 + 3):
                source = [rng.randrange(-mod, mod) for _ in range(size)]
                original = source[:], modulus[:]
                result = [1]
                for exponent in range(8):
                    assert polynomial_pow_mod(source, exponent, modulus, mod) == result
                    result = poly_mod(fps_multiply(result, source, mod), modulus, mod)
                assert (source, modulus) == original


def test_inverse_and_negative_power():
    for degree in (3, 64, 65, 129):
        modulus = [1] + [0] * (degree - 1) + [1]
        source = [0, 1]
        inverse = polynomial_inverse_mod(source, modulus)
        assert poly_mod(fps_multiply(source, inverse), modulus) == [1]
        assert polynomial_pow_mod(source, -1, modulus) == inverse
        assert polynomial_pow_mod(source, -5, modulus) == polynomial_pow_mod(inverse, 5, modulus)
    with pytest.raises(ZeroDivisionError):
        polynomial_pow_mod([0, 1], -1, [0, 0, 1])
    for modulus in ([], [0], [1]):
        with pytest.raises(ValueError):
            polynomial_pow_mod([1], 2, modulus)
        with pytest.raises(ValueError):
            polynomial_inverse_mod([1], modulus)
