"""2つの多項式のresultantを計算する。"""

from library_codex.fps.FormalPowerSeries import DEFAULT_MOD, fps_shrink
from library_codex.polynomial.PolynomialDivision import poly_divmod
from library_codex.polynomial._HalfGCD import (
    FAST_GCD_THRESHOLD,
    polynomial_gcd_matrix,
)

def polynomial_resultant(first, second, mod=DEFAULT_MOD):
    """Resultant over a field, computed by an iterative Euclidean chain."""
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    if not first:
        return 1 if len(second) == 1 else 0
    if not second:
        return 1 if len(first) == 1 else 0
    if max(len(first), len(second)) < FAST_GCD_THRESHOLD:
        result = 1
        sign = 0
        while True:
            _, remainder = poly_divmod(first, second, mod)
            first_degree = len(first) - 1
            second_degree = len(second) - 1
            if not remainder:
                if second_degree == 0:
                    result = result * pow(
                        second[0], first_degree, mod
                    ) % mod
                else:
                    result = 0
                break
            remainder_degree = len(remainder) - 1
            if first_degree & second_degree & 1:
                sign ^= 1
            result = result * pow(
                second[-1], first_degree - remainder_degree, mod
            ) % mod
            first, second = second, remainder
        return -result % mod if sign else result
    _, pair, quotients = polynomial_gcd_matrix(first, second, mod)
    if len(pair[0]) > 1:
        return 0
    result = 1
    sign = 0
    first_degree = len(first) - 1
    second_degree = len(second) - 1
    leading = second[-1] % mod
    for index, quotient in enumerate(quotients):
        if index + 1 == len(quotients):
            if second_degree == 0:
                result = result * pow(leading, first_degree, mod) % mod
            else:
                result = 0
            break
        next_quotient = quotients[index + 1]
        remainder_degree = second_degree - (len(next_quotient) - 1)
        if first_degree & second_degree & 1:
            sign ^= 1
        result = result * pow(
            leading, first_degree - remainder_degree, mod
        ) % mod
        leading = leading * pow(next_quotient[-1], -1, mod) % mod
        first_degree, second_degree = second_degree, remainder_degree
    return -result % mod if sign else result
