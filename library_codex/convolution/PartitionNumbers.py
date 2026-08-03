"""整数分割数列を生成する。"""

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

def partition_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    denominator = [0] * (max_index + 1)
    denominator[0] = 1
    index = 1
    while True:
        lower = index * (3 * index - 1) // 2
        if lower > max_index:
            break
        value = -1 if index & 1 else 1
        denominator[lower] = value % mod
        upper = index * (3 * index + 1) // 2
        if upper <= max_index:
            denominator[upper] = value % mod
        index += 1
    return fps_inverse(denominator, max_index + 1, mod)

