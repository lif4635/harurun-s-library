"""多項式のmonic化・gcd・拡張gcdを計算する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_multiply,
    fps_shrink,
    fps_subtract,
)
from library_codex.polynomial.PolynomialDivision import poly_divmod, poly_mod
from library_codex.polynomial._HalfGCD import (
    FAST_GCD_THRESHOLD,
    polynomial_gcd_matrix,
)

def polynomial_monic(polynomial, mod=DEFAULT_MOD):
    result = fps_shrink(polynomial, mod)
    if not result:
        return []
    inverse = pow(result[-1], -1, mod)
    return [value * inverse % mod for value in result]

def polynomial_gcd(first, second, mod=DEFAULT_MOD):
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    if max(len(first), len(second)) < FAST_GCD_THRESHOLD:
        while second:
            first, second = second, poly_mod(first, second, mod)
        return polynomial_monic(first, mod)
    _, pair, _ = polynomial_gcd_matrix(first, second, mod)
    return polynomial_monic(pair[0], mod)

def polynomial_extended_gcd(first, second, mod=DEFAULT_MOD):
    """Return monic g, s, t satisfying s * first + t * second = g."""
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    if max(len(first), len(second)) < FAST_GCD_THRESHOLD:
        old_remainder = first
        remainder = second
        old_first, current_first = [1], []
        old_second, current_second = [], [1]
        while remainder:
            quotient, next_remainder = poly_divmod(
                old_remainder, remainder, mod
            )
            old_remainder, remainder = remainder, next_remainder
            old_first, current_first = current_first, fps_subtract(
                old_first, fps_multiply(quotient, current_first, mod), mod
            )
            old_second, current_second = current_second, fps_subtract(
                old_second, fps_multiply(quotient, current_second, mod), mod
            )
            old_first = fps_shrink(old_first, mod)
            old_second = fps_shrink(old_second, mod)
            current_first = fps_shrink(current_first, mod)
            current_second = fps_shrink(current_second, mod)
        if not old_remainder:
            return [], [], []
        scale = pow(old_remainder[-1], -1, mod)
        return (
            [value * scale % mod for value in old_remainder],
            [value * scale % mod for value in old_first],
            [value * scale % mod for value in old_second],
        )
    matrix, pair, _ = polynomial_gcd_matrix(first, second, mod)
    gcd = pair[0]
    if not gcd:
        return [], [], []
    scale = pow(gcd[-1], -1, mod)
    return (
        [value * scale % mod for value in gcd],
        [value * scale % mod for value in matrix[0]],
        [value * scale % mod for value in matrix[1]],
    )
