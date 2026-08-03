"""多項式列へMöbius型変換を適用する。"""

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_power,
    fps_shrink,
    fps_taylor_shift,
)

from library_codex.convolution.PolynomialComposition import fps_compose

def polynomial_mobius_transform(polynomial, a, b, c, d, degree=None,
                                mod=DEFAULT_MOD):
    """Formal expansion of f((a+b*x)/(c+d*x)); requires c != 0."""
    if degree is None:
        degree = len(polynomial)
    c %= mod
    if c == 0:
        raise ValueError("the denominator must have a nonzero constant term")
    denominator_inverse = fps_inverse([c, d % mod], degree, mod)
    inner = fps_multiply([a % mod, b % mod], denominator_inverse, mod)[:degree]
    return fps_compose(polynomial, inner, degree, mod)

