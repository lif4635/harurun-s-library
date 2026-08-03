"""列へEuler変換または逆変換を適用する。"""

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

def euler_transform(values, mod=DEFAULT_MOD):
    """Coefficients of product((1-x**k)**(-values[k]))."""
    size = len(values)
    logarithm = [0] * size
    for divisor in range(1, size):
        contribution = divisor * values[divisor] % mod
        for multiple in range(divisor, size, divisor):
            logarithm[multiple] += contribution
    for index in range(1, size):
        logarithm[index] = logarithm[index] % mod * pow(index, -1, mod) % mod
    return fps_exponential(logarithm, size, mod)

