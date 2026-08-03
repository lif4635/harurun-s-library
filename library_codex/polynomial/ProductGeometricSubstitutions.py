"""多項式へ等比数列を代入した値の積を計算する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

def product_geometric_substitutions(polynomial, ratio, count,
                                    degree=None, mod=DEFAULT_MOD):
    """Product of f(ratio**k*x), 0 <= k < count, as a truncated FPS."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if degree is None:
        degree = len(polynomial)
    if degree == 0:
        return []
    if not polynomial or polynomial[0] % mod != 1:
        raise ValueError("the constant coefficient must be one")
    if count == 0:
        return [1] + [0] * (degree - 1)
    logarithm = fps_logarithm(polynomial, degree, mod)
    ratio %= mod
    power = 1
    count_power = 1
    ratio_to_count = pow(ratio, count, mod)
    for index in range(1, degree):
        power = power * ratio % mod
        count_power = count_power * ratio_to_count % mod
        if power == 1:
            multiplier = count % mod
        else:
            multiplier = ((count_power - 1) * pow(power - 1, -1, mod)) % mod
        logarithm[index] = logarithm[index] * multiplier % mod
    return fps_exponential(logarithm, degree, mod)

