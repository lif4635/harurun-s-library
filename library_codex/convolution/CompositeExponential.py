"""合成指数型母関数とその逆変換を計算する。"""

from library_codex.convolution.SumOfRationals import sum_of_rationals

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

def composite_exponential(polynomial, degree, mod=DEFAULT_MOD):
    """Return the first ``degree`` coefficients of f(exp(x))."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    fractions = [
        ([coefficient % mod], [1, -index % mod])
        for index, coefficient in enumerate(polynomial)
    ]
    numerator, denominator = sum_of_rationals(fractions, mod)
    result = fps_multiply(
        numerator,
        fps_inverse(denominator, degree, mod),
        mod,
    )[:degree]
    result.extend([0] * (degree - len(result)))
    inverse_factorial = 1
    for index in range(1, degree):
        inverse_factorial = inverse_factorial * pow(index, -1, mod) % mod
        result[index] = result[index] * inverse_factorial % mod
    return result

def composite_exponential_scaled(polynomial, scale=1, degree=None,
                                 mod=DEFAULT_MOD):
    """Return f(exp(scale*x)) modulo x**degree."""
    if degree is None:
        degree = len(polynomial)
    if scale % mod == 0:
        raise ValueError("scale must be nonzero")
    if degree == 0 or not polynomial:
        return []
    fractions = [
        ([coefficient % mod], [1, -scale * index % mod])
        for index, coefficient in enumerate(polynomial)
    ]
    numerator, denominator = sum_of_rationals(fractions, mod)
    result = fps_multiply(
        numerator, fps_inverse(denominator, degree, mod), mod
    )[:degree]
    result.extend([0] * (degree - len(result)))
    inverse_factorial = 1
    for index in range(1, degree):
        inverse_factorial = inverse_factorial * pow(index, -1, mod) % mod
        result[index] = result[index] * inverse_factorial % mod
    return result

def inverse_composite_exponential(series, scale=1, mod=DEFAULT_MOD):
    """Invert ``composite_exponential_scaled`` for equal input/output size."""
    size = len(series)
    if size == 0:
        return []
    scale %= mod
    if scale == 0:
        raise ValueError("scale must be nonzero")
    moments = [0] * size
    factorial = 1
    for index, value in enumerate(series):
        if index:
            factorial = factorial * index % mod
        moments[index] = value * factorial % mod
    points = [scale * index % mod for index in range(size)]
    tree = ProductTree(points, mod)
    reversed_denominator = tree.polynomial[::-1]
    numerator = fps_multiply(moments, reversed_denominator, mod)[:size]
    evaluations = tree.evaluate(numerator[::-1])
    factorials = [1] * size
    for index in range(1, size):
        factorials[index] = factorials[index - 1] * index % mod
    scale_power = pow(scale, size - 1, mod)
    result = [0] * size
    last = size - 1
    for index in range(size):
        denominator = (scale_power * factorials[index] % mod
                       * factorials[last - index] % mod)
        if (last - index) & 1:
            denominator = -denominator % mod
        result[index] = evaluations[index] * pow(denominator, -1, mod) % mod
    return result

