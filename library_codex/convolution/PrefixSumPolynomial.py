"""多項式値列のprefix和を表す多項式を求める。"""

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

from library_codex.convolution.MultipointEvaluation import (
    ProductTree,
    interpolate_consecutive,
)

def prefix_sum_polynomial(polynomial, mod=DEFAULT_MOD):
    """Coefficients of g(x)=sum(0 <= y <= x, f(y))."""
    if not polynomial:
        return []
    count = len(polynomial) + 1
    tree = ProductTree(range(count), mod)
    values = tree.evaluate(polynomial)
    for index in range(1, count):
        values[index] = (values[index] + values[index - 1]) % mod
    return tree.interpolate(values)

