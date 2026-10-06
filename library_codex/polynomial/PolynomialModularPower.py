"""多項式を別の多項式で割った剰余環上の逆元と冪を計算する。"""

from library_codex.polynomial.PolynomialGCD import polynomial_extended_gcd

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_inverse,
    fps_multiply,
    fps_shrink,
)
from library_codex.polynomial.PolynomialDivision import poly_mod

def polynomial_inverse_mod(polynomial, modulus, mod=DEFAULT_MOD):
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    gcd, inverse, _ = polynomial_extended_gcd(polynomial, modulus, mod)
    if gcd != [1]:
        raise ZeroDivisionError("polynomial is not invertible modulo modulus")
    return poly_mod(inverse, modulus, mod)

def polynomial_pow_mod(polynomial, exponent, modulus, mod=DEFAULT_MOD):
    if exponent < 0:
        polynomial = polynomial_inverse_mod(polynomial, modulus, mod)
        exponent = -exponent
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    result = [1]
    base = poly_mod(polynomial, modulus, mod)
    degree = len(modulus) - 1
    if degree <= 63:
        leading_inverse = pow(modulus[-1], -1, mod)
        inverse = None
    else:
        leading_inverse = 0
        inverse = fps_inverse(modulus[::-1], degree - 1, mod) if exponent > 1 else []
    while exponent:
        if exponent & 1:
            result = _reduce(fps_multiply(result, base, mod), modulus, inverse, leading_inverse, mod)
        exponent >>= 1
        if exponent:
            base = _reduce(fps_multiply(base, base, mod), modulus, inverse, leading_inverse, mod)
    return result


def _reduce(values, modulus, inverse, leading_inverse, mod):
    degree = len(modulus) - 1
    size = len(values) - degree
    if size > 0:
        if inverse is None:
            for index in range(size - 1, -1, -1):
                value = values[index + degree] * leading_inverse % mod
                for offset in range(degree):
                    values[index + offset] = (values[index + offset] - value * modulus[offset]) % mod
        else:
            quotient = fps_multiply(values[:degree-1:-1], inverse[:size], mod)[:size]
            quotient.reverse()
            product = fps_multiply(quotient, modulus, mod)
            for index in range(degree):
                values[index] = (values[index] - product[index]) % mod
        del values[degree:]
    while values and not values[-1]:
        values.pop()
    return values
