"""多項式を別の多項式で割った剰余環上の逆元と冪を計算する。"""

from library_codex.polynomial.PolynomialGCD import polynomial_extended_gcd

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_divmod,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_remainder,
    fps_shrink,
    fps_subtract,
    fps_taylor_shift,
)

def polynomial_inverse_mod(polynomial, modulus, mod=DEFAULT_MOD):
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    gcd, inverse, _ = polynomial_extended_gcd(polynomial, modulus, mod)
    if gcd != [1]:
        raise ZeroDivisionError("polynomial is not invertible modulo modulus")
    return fps_remainder(inverse, modulus, mod)

def polynomial_pow_mod(polynomial, exponent, modulus, mod=DEFAULT_MOD):
    if exponent < 0:
        polynomial = polynomial_inverse_mod(polynomial, modulus, mod)
        exponent = -exponent
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    result = [1]
    base = fps_remainder(polynomial, modulus, mod)
    while exponent:
        if exponent & 1:
            result = fps_remainder(fps_multiply(result, base, mod), modulus, mod)
        exponent >>= 1
        if exponent:
            base = fps_remainder(fps_multiply(base, base, mod), modulus, mod)
    return result

