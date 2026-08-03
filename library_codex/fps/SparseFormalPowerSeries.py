"""非零項が少ない形式的冪級数の逆数・除算・exp・log・冪を計算する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_power,
    fps_shrink,
    fps_taylor_shift,
)

def sparse_inverse(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    if not series or series[0] % mod == 0:
        raise ZeroDivisionError("constant coefficient must be invertible")
    inverse_constant = pow(series[0] % mod, -1, mod)
    terms = [(index, value % mod) for index, value in enumerate(series[1:], 1)
             if value % mod]
    result = [0] * degree
    result[0] = inverse_constant
    for index in range(1, degree):
        value = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            value += coefficient * result[index - offset]
        result[index] = -value * inverse_constant % mod
    return result

def sparse_divide(numerator, denominator, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(numerator)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if not denominator or denominator[0] % mod == 0:
        raise ZeroDivisionError("constant coefficient must be invertible")
    inverse_constant = pow(denominator[0] % mod, -1, mod)
    terms = [(index, value * inverse_constant % mod)
             for index, value in enumerate(denominator[1:], 1) if value % mod]
    result = [0] * degree
    for index in range(degree):
        value = numerator[index] % mod if index < len(numerator) else 0
        value = value * inverse_constant % mod
        for offset, coefficient in terms:
            if offset > index:
                break
            value -= result[index - offset] * coefficient
        result[index] = value % mod
    return result

def sparse_exponential(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree == 0:
        return []
    if series and series[0] % mod:
        raise ValueError("constant coefficient must be zero")
    terms = [(index, value % mod) for index, value in enumerate(series[1:], 1)
             if value % mod]
    result = [0] * degree
    result[0] = 1
    for index in range(1, degree):
        value = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            value += offset * coefficient * result[index - offset]
        result[index] = value % mod * pow(index, -1, mod) % mod
    return result

def sparse_logarithm(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree == 0:
        return []
    if not series or series[0] % mod != 1:
        raise ValueError("constant coefficient must be one")
    derivative = [index * value % mod for index, value in enumerate(series)][1:]
    quotient = sparse_divide(derivative, series, max(0, degree - 1), mod)
    result = [0] * degree
    for index, value in enumerate(quotient, 1):
        result[index] = value * pow(index, -1, mod) % mod
    return result

def sparse_power(series, exponent, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if exponent < 0:
        series = sparse_inverse(series, degree, mod)
        exponent = -exponent
    if exponent == 0:
        return [1] + [0] * max(0, degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % mod == 0:
        leading += 1
    shift = leading * exponent
    if leading == len(series) or shift >= degree:
        return [0] * degree
    constant = series[leading] % mod
    inverse_constant = pow(constant, -1, mod)
    normalized = [value * inverse_constant % mod for value in series[leading:]]
    logarithm = sparse_logarithm(normalized, degree - shift, mod)
    factor = exponent % mod
    logarithm = [value * factor % mod for value in logarithm]
    result = sparse_exponential(logarithm, degree - shift, mod)
    scale = pow(constant, exponent, mod)
    return [0] * shift + [value * scale % mod for value in result]

