"""Bell数列を生成する。"""

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

def bell_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    factorial, inverse_factorial = _factorials(max_index, mod)
    series = [0] + inverse_factorial[1:]
    values = fps_exponential(series, max_index + 1, mod)
    return [values[index] * factorial[index] % mod
            for index in range(max_index + 1)]

