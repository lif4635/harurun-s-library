"""第一種・第二種Stirling数の行または列を生成する。"""

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

def _factorials(size, mod):
    if size >= mod:
        raise ValueError("series degree must be smaller than mod")
    factorial = [1] * (size + 1)
    for index in range(1, size + 1):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * (size + 1)
    if size:
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(size, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
    return factorial, inverse_factorial

def stirling_first_row(order, mod=DEFAULT_MOD, signed=False):
    """Coefficients of rising factorial x(x+1)...(x+order-1)."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    if order == 0:
        return [1]
    polynomial = [0, 1]
    for bit in range(order.bit_length() - 2, -1, -1):
        current = order >> bit
        shifted = fps_taylor_shift(polynomial, current >> 1, mod)
        polynomial = fps_multiply(polynomial, shifted, mod)
        if current & 1:
            result = [0] * (len(polynomial) + 1)
            scale = current - 1
            for index, value in enumerate(polynomial):
                result[index] = (result[index] + value * scale) % mod
                result[index + 1] = (result[index + 1] + value) % mod
            polynomial = result
    if signed:
        for index in range(order + 1):
            if (order - index) & 1:
                polynomial[index] = -polynomial[index] % mod
    return polynomial

def stirling_second_row(order, mod=DEFAULT_MOD):
    """Return S(order, 0), ..., S(order, order)."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    factorial, inverse_factorial = _factorials(order, mod)
    powers = [pow(index, order, mod) * inverse_factorial[index] % mod
              for index in range(order + 1)]
    signs = [(-inverse_factorial[index] if index & 1 else inverse_factorial[index]) % mod
             for index in range(order + 1)]
    return fps_multiply(powers, signs, mod)[:order + 1]

def stirling_first_column(column, upper, mod=DEFAULT_MOD):
    """Unsigned first-kind Stirling numbers s(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError("indices must be nonnegative")
    if upper < column:
        return []
    factorial, inverse_factorial = _factorials(upper, mod)
    logarithm = [0] + [pow(index, -1, mod) for index in range(1, upper + 1)]
    values = fps_power(logarithm, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result

def stirling_second_column(column, upper, mod=DEFAULT_MOD):
    """Second-kind Stirling numbers S(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError("indices must be nonnegative")
    if upper < column:
        return []
    factorial, inverse_factorial = _factorials(upper, mod)
    exponential_minus_one = [0] + inverse_factorial[1:]
    values = fps_power(exponential_minus_one, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result

