"""低次数の多項式から逆数・log・exp・整数冪の遠い係数だけを求める。"""

from library_codex.combinatorial_series.LinearRecurrence import bostan_mori
from library_codex.fps.SparseFormalPowerSeries import sparse_exponential, sparse_power
from library_codex.polynomial.PolynomialMatrixRecurrence import linear_matrix_recurrence


def _polynomial(series, index, mod):
    if index < 0 or mod < 2:
        raise ValueError("require index >= 0 and mod >= 2")
    result = [value % mod for value in series[:index + 1]]
    while result and result[-1] == 0:
        result.pop()
    return result


def inv_coeff(series, index, mod=998244353):
    """1/seriesのx^indexの係数を返す。indexまでの係数列は作らない。"""
    series = _polynomial(series, index, mod)
    if not series or series[0] == 0:
        raise ZeroDivisionError("constant coefficient must be invertible")
    return bostan_mori(index, [1], series, mod)


def log_coeff(series, index, mod=998244353):
    """定数項1のseriesのlogからx^indexの係数を返す。"""
    series = _polynomial(series, index, mod)
    if not series or series[0] != 1 or index >= mod:
        raise ValueError("require constant 1 and index < mod")
    if index == 0:
        return 0
    derivative = [i * series[i] % mod for i in range(1, len(series))]
    return bostan_mori(index - 1, derivative, series, mod) * pow(index, -1, mod) % mod


def exp_coeff(series, index, mod=998244353):
    """定数項0のseriesのexpからx^indexの係数を返す。"""
    series = _polynomial(series, index, mod)
    if index >= mod or series and series[0]:
        raise ValueError("require constant 0 and index < mod")
    if index == 0:
        return 1
    if not series:
        return 0
    dimension = len(series) - 1
    if index <= 64 or dimension > 8:
        return sparse_exponential(series, index + 1, mod)[index]
    initial = sparse_exponential(series, dimension, mod)
    a, b = [[0] * dimension for _ in range(dimension)], [[0] * dimension for _ in range(dimension)]
    for i in range(dimension - 1):
        a[i][i + 1], b[i][i + 1] = dimension, 1
    for k in range(1, dimension + 1):
        a[-1][dimension - k] = k * series[k] % mod
    return linear_matrix_recurrence(initial, a, b, (dimension, 1), index - dimension + 1, mod)[-1]


def pow_coeff(series, exponent, index, mod=998244353):
    """seriesの非負整数冪からx^indexの係数を返す。"""
    series = _polynomial(series, index, mod)
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    if exponent == 0:
        return int(index == 0)
    if not series:
        return 0
    order = next(i for i, value in enumerate(series) if value)
    index -= order * exponent
    if index < 0 or index > (len(series) - 1 - order) * exponent:
        return 0
    series = series[order:order + index + 1]
    if index == 0:
        return pow(series[0], exponent, mod)
    if index >= mod:
        raise ValueError("shifted index must be less than mod")
    dimension = len(series) - 1
    if dimension == 0:
        return 0
    if index <= 64 or dimension > 8:
        return sparse_power(series, exponent, index + 1, mod)[index]
    initial = sparse_power(series, exponent, dimension, mod)
    a, b = [[0] * dimension for _ in range(dimension)], [[0] * dimension for _ in range(dimension)]
    for i in range(dimension - 1):
        a[i][i + 1], b[i][i + 1] = dimension * series[0] % mod, series[0]
    for k in range(1, dimension + 1):
        a[-1][dimension - k] = ((exponent + 1) * k - dimension) * series[k] % mod
        b[-1][dimension - k] = -series[k] % mod
    return linear_matrix_recurrence(initial, a, b, (dimension * series[0] % mod, series[0]), index - dimension + 1, mod)[-1]
