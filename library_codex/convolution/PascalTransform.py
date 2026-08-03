"""列へPascal変換または逆変換を適用する。"""

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

def pascal_transform(values, inverse=False, transpose=False, mod=DEFAULT_MOD):
    """Apply binom(i,j), or its transpose; inverse toggles binomial inversion."""
    size = len(values)
    if size == 0:
        return []
    factorial, inverse_factorial = _factorials(size - 1, mod)
    sign = -1 if inverse else 1
    kernel = [inverse_factorial[index] * (sign if index & 1 else 1) % mod
              for index in range(size)]
    if not transpose:
        scaled = [values[index] * inverse_factorial[index] % mod
                  for index in range(size)]
        product = fps_multiply(scaled, kernel, mod)[:size]
        return [product[index] * factorial[index] % mod for index in range(size)]
    scaled = [values[index] * factorial[index] % mod for index in range(size)]
    scaled.reverse()
    product = fps_multiply(scaled, kernel, mod)[:size]
    product.reverse()
    return [product[index] * inverse_factorial[index] % mod
            for index in range(size)]

