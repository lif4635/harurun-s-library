"""相異なる一次因子に対する部分分数分解を計算する。"""

from library_codex.convolution.FormalPowerSeries import (
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

from library_codex.convolution.MultipointEvaluation import ProductTree

def partial_fraction_distinct(numerator, roots, mod=DEFAULT_MOD):
    """Coefficients a_i for f(x) / product(x-b_i) = sum a_i/(x-b_i)."""
    tree = ProductTree(roots, mod)
    if len(numerator) > len(roots):
        raise ValueError("numerator degree must be smaller than denominator degree")
    numerator_values = tree.evaluate(numerator)
    derivative_values = tree.evaluate(fps_derivative(tree.polynomial, mod))
    result = [0] * len(roots)
    for index, denominator in enumerate(derivative_values):
        if denominator == 0:
            raise ValueError("roots must be distinct modulo mod")
        result[index] = numerator_values[index] * pow(denominator, -1, mod) % mod
    return result

