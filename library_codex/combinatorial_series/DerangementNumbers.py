"""完全順列数列を生成する。"""

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

def derangement_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    result = [0] * (max_index + 1)
    result[0] = 1
    if max_index:
        result[1] = 0
    for index in range(2, max_index + 1):
        result[index] = (index - 1) * (result[index - 1] + result[index - 2]) % mod
    return result

