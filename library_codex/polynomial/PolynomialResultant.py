"""2つの多項式のresultantを計算する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_shrink,
    fps_subtract,
    fps_taylor_shift,
)
from library_codex.polynomial.PolynomialDivision import poly_divmod

def polynomial_resultant(first, second, mod=DEFAULT_MOD):
    """Resultant over a field, computed by an iterative Euclidean chain."""
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    if not first:
        return 1 if len(second) == 1 else 0
    if not second:
        return 1 if len(first) == 1 else 0
    result = 1
    sign = 0
    while True:
        _, remainder = poly_divmod(first, second, mod)
        first_degree = len(first) - 1
        second_degree = len(second) - 1
        if not remainder:
            if second_degree == 0:
                result = result * pow(second[0], first_degree, mod) % mod
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
