"""多項式値列のprefix和を補間して求める。"""

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

from library_codex.polynomial.MultipointEvaluation import ProductTree

def polynomial_prefix_sum(polynomial, mod=DEFAULT_MOD, inclusive=False):
    """Polynomial g with g(n)=sum(f(i), 0 <= i < n), or through n if inclusive."""
    polynomial = fps_shrink(polynomial, mod)
    if not polynomial:
        return []
    size = len(polynomial) + 1
    points = list(range(size))
    values = ProductTree(points, mod).evaluate(polynomial)
    samples = [0] * size
    for index in range(1, size):
        samples[index] = (samples[index - 1] + values[index - 1]) % mod
    result = ProductTree(points, mod).interpolate(samples)
    result = fps_shrink(result, mod)
    if inclusive:
        result = fps_taylor_shift(result, 1, mod)
    return fps_shrink(result, mod)
